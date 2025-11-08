/**
 * Supabase Edge Function: generate-report
 * 
 * Remplace le scénario Make.com post-paiement Stripe
 * Déclenché via webhook Stripe charge.succeeded
 * 
 * Chemin: supabase/functions/generate-report/index.ts
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.38.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  // Handle CORS
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    // 1. PARSE WEBHOOK STRIPE
    const signature = req.headers.get("stripe-signature");
    const body = await req.text();

    // Vérifier signature Stripe (optionnel mais recommandé)
    // const event = stripe.webhooks.constructEvent(body, signature, STRIPE_WEBHOOK_SECRET);

    const event = JSON.parse(body);

    // 2. RÉCUPÉRER LES DONNÉES DU PAIEMENT
    if (event.type !== "charge.succeeded") {
      return new Response(JSON.stringify({ ok: true }), { headers: corsHeaders });
    }

    const charge = event.data.object;
    
    // Métadonnées Stripe (passées lors de la création du paiement)
    const userId = charge.metadata.user_id;
    const userEmail = charge.metadata.user_email;
    const userName = charge.metadata.user_name;

    console.log(`🎯 Génération de rapport pour ${userName} (${userEmail})`);

    // 3. INITIALISER SUPABASE
    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    
    const supabase = createClient(supabaseUrl, supabaseServiceKey, {
      auth: { persistSession: false },
    });

    // 4. RÉCUPÉRER LES DONNÉES UTILISATEUR
    // Récupérer colorimétrie + morphologie + photos + préférences
    const { data: userProfile, error: profileError } = await supabase
      .from("user_profiles")
      .select(
        `
        id,
        first_name,
        email,
        colorimetry (season, undertone, colors),
        morphology (type, measurements),
        photos (urls),
        brand_preferences (preferred_brands)
        `
      )
      .eq("id", userId)
      .single();

    if (profileError) {
      console.error("❌ Erreur récupération profil:", profileError);
      throw new Error(`Profil utilisateur non trouvé: ${userId}`);
    }

    console.log("✅ Profil utilisateur récupéré");

    // 5. APPELER OPENAI POUR GÉNÉRER LE CONTENU DU RAPPORT
    // (Ce sera un appel asynchrone aux modules GPT)
    const reportContent = await generateReportWithOpenAI({
      user: userProfile,
      userName,
      userEmail,
    });

    console.log("✅ Contenu du rapport généré par OpenAI");

    // 6. CRÉER LE PDF À PARTIR DU CONTENU
    const pdfBuffer = await generatePDFFromHTML(reportContent);

    console.log("✅ PDF généré");

    // 7. UPLOAD LE PDF SUR SUPABASE STORAGE
    const fileName = `reports/${userId}_${Date.now()}.pdf`;
    
    const { data: uploadData, error: uploadError } = await supabase.storage
      .from("stylist-reports")
      .upload(fileName, pdfBuffer, {
        contentType: "application/pdf",
        cacheControl: "3600",
      });

    if (uploadError) {
      console.error("❌ Erreur upload PDF:", uploadError);
      throw uploadError;
    }

    console.log("✅ PDF uploadé:", fileName);

    // 8. CRÉER LE LIEN PUBLIC TÉLÉCHARGEABLE
    const { data: publicUrl } = supabase.storage
      .from("stylist-reports")
      .getPublicUrl(fileName);

    console.log("✅ Lien public généré");

    // 9. ENREGISTRER LE RAPPORT EN BASE DE DONNÉES
    const { error: insertError } = await supabase
      .from("reports")
      .insert({
        user_id: userId,
        file_path: fileName,
        public_url: publicUrl.publicUrl,
        status: "completed",
        generated_at: new Date().toISOString(),
      });

    if (insertError) {
      console.error("❌ Erreur insertion rapport:", insertError);
      throw insertError;
    }

    console.log("✅ Rapport enregistré en DB");

    // 10. ENVOYER EMAIL AVEC LE LIEN
    const emailSent = await sendReportEmail({
      email: userEmail,
      name: userName,
      downloadUrl: publicUrl.publicUrl,
    });

    if (!emailSent) {
      console.warn("⚠️ Email non envoyé, mais rapport généré");
    } else {
      console.log("✅ Email envoyé");
    }

    // 11. RETOURNER SUCCÈS
    return new Response(
      JSON.stringify({
        ok: true,
        message: "Rapport généré avec succès",
        report_url: publicUrl.publicUrl,
      }),
      {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("❌ Erreur Edge Function:", error);
    
    return new Response(
      JSON.stringify({
        ok: false,
        error: error.message,
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});

/**
 * FONCTION 1: Générer le contenu du rapport avec OpenAI
 * Remplace les 7 modules Make.com GPT
 */
async function generateReportWithOpenAI({ user, userName, userEmail }) {
  const openaiApiKey = Deno.env.get("OPENAI_API_KEY");

  // Construire le prompt système complet
  const systemPrompt = `Tu es une styliste experte en conseil d'image personnalisé.
Génère un rapport stylistique complet au format HTML pur.

IMPORTANT:
- Génère UNIQUEMENT du HTML pur, pas de markdown
- Pas de balises markdown (\\`\\`\\`html, \\`\\`\\`)
- Chaque section doit commencer par un page-break
- Format strict: <div>, <h1>, <p>, <table> uniquement
- Aucune balise custom`;

  const userPrompt = `Génère le rapport stylistique complet pour:
Prénom: ${user.first_name}
Email: ${userEmail}

Saison colorimétrique: ${user.colorimetry.season}
Sous-tons: ${user.colorimetry.undertone}
Couleurs palette: ${user.colorimetry.colors.join(", ")}

Type morphologie: ${user.morphology.type}
Mesures: ${JSON.stringify(user.morphology.measurements)}

STRUCTURE REQUISE (10 SECTIONS):
1. Page de couverture personnalisée
2. Colorimétrie détaillée (saison + palette + conseils maquillage)
3. Morphologie (analyse + schéma + recommandations)
4. Profil stylistique (archétypes + analyse)
5. Garde-robe capsule (20 basics + 5 statements)
6. Mix & match (10 formules)
7. Guide shopping (marques recommandées)
8. Occasions spécifiques (5 looks)
9. FAQ
10. Conclusion + checklist

Chaque section DOIT:
- Être personnalisée avec les vraies données
- Avoir des conseils concrets et actionnables
- Inclure des références à des marques/produits
- Être formatée en HTML pur`;

  try {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${openaiApiKey}`,
      },
      body: JSON.stringify({
        model: "gpt-4-turbo",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt },
        ],
        max_tokens: 8000,
        temperature: 0.7,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.statusText}`);
    }

    const data = await response.json();
    const htmlContent = data.choices[0].message.content;

    // Nettoyer le contenu (supprimer les balises markdown si présentes)
    const cleanedContent = htmlContent
      .replace(/```html\n?/g, "")
      .replace(/```\n?/g, "")
      .trim();

    return cleanedContent;
  } catch (error) {
    console.error("❌ Erreur OpenAI:", error);
    throw error;
  }
}

/**
 * FONCTION 2: Générer le PDF à partir du HTML
 * Utilise html2pdf via Node.js worker ou API externe
 */
async function generatePDFFromHTML(htmlContent) {
  // Option A: Utiliser une API externe (recommandé pour Edge Functions)
  // Option B: Utiliser pdf-lib (pour assembler des PDFs)
  
  // Ici on va utiliser une API externe pour convertir HTML -> PDF
  const htmlToPdfApiKey = Deno.env.get("HTML_TO_PDF_API_KEY");
  const htmlToPdfEndpoint = "https://api.html2pdf.app/v1/generate";

  try {
    const response = await fetch(htmlToPdfEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-KEY": htmlToPdfApiKey,
      },
      body: JSON.stringify({
        html: htmlContent,
        options: {
          format: "A4",
          margin: "10mm",
          printBackground: true,
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`HTML2PDF error: ${response.statusText}`);
    }

    const pdfBuffer = await response.arrayBuffer();
    return new Uint8Array(pdfBuffer);
  } catch (error) {
    console.error("❌ Erreur PDF generation:", error);
    throw error;
  }
}

/**
 * FONCTION 3: Envoyer l'email avec le lien de téléchargement
 */
async function sendReportEmail({ email, name, downloadUrl }) {
  const resendApiKey = Deno.env.get("RESEND_API_KEY");

  const emailHtml = `
    <h2>Bienvenue ${name}!</h2>
    <p>Votre rapport stylistique MyStylist.io est prêt ✨</p>
    <p><a href="${downloadUrl}" style="background:#9b59b6;color:white;padding:12px 30px;text-decoration:none;border-radius:5px;display:inline-block;">
      📥 Télécharger mon rapport (PDF)
    </a></p>
    <p style="color:#7f8c8d;font-size:14px;">
      Ce lien reste valide 30 jours. Conservez-le précieusement !
    </p>
  `;

  try {
    const response = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${resendApiKey}`,
      },
      body: JSON.stringify({
        from: "reports@mystylist.io",
        to: email,
        subject: "✨ Votre rapport stylistique MyStylist.io",
        html: emailHtml,
      }),
    });

    return response.ok;
  } catch (error) {
    console.error("❌ Erreur Resend:", error);
    return false;
  }
}
