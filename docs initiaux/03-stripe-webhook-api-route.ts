/**
 * pages/api/webhooks/stripe.ts
 * 
 * Webhook Stripe: déclenche la génération du rapport après paiement réussi
 * 
 * Remplace complètement le scénario Make.com
 * - Reçoit l'événement charge.succeeded
 * - Déclenche l'Edge Function Supabase
 * - Enregistre le statut en base
 */

import type { NextApiRequest, NextApiResponse } from "next";
import Stripe from "stripe";
import { createClient } from "@supabase/supabase-js";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || "", {
  apiVersion: "2023-10-16",
});

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL || "",
  process.env.SUPABASE_SERVICE_ROLE_KEY || ""
);

const STRIPE_WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET || "";
const SUPABASE_FUNCTION_URL = process.env.SUPABASE_FUNCTION_URL || "";

type ResponseData = {
  received?: boolean;
  error?: string;
};

/**
 * HANDLER WEBHOOK
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const signature = req.headers["stripe-signature"];

  let event;

  try {
    // 1. VÉRIFIER LA SIGNATURE STRIPE
    event = stripe.webhooks.constructEvent(
      req.body,
      signature as string,
      STRIPE_WEBHOOK_SECRET
    );
  } catch (error) {
    console.error("❌ Stripe signature error:", error);
    return res.status(400).json({ error: "Invalid signature" });
  }

  try {
    // 2. FILTRER LES ÉVÉNEMENTS PERTINENTS
    switch (event.type) {
      case "charge.succeeded":
        await handleChargeSucceeded(event.data.object as Stripe.Charge);
        break;

      case "charge.failed":
        await handleChargeFailed(event.data.object as Stripe.Charge);
        break;

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    // 3. RETOURNER SUCCÈS À STRIPE
    res.status(200).json({ received: true });
  } catch (error) {
    console.error("❌ Webhook handler error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
}

/**
 * HANDLER: Paiement réussi
 * → Déclenche la génération du rapport
 */
async function handleChargeSucceeded(charge: Stripe.Charge) {
  console.log(`✅ Charge succeeded: ${charge.id}`);

  try {
    // 1. EXTRAIRE LES MÉTADONNÉES DU PAIEMENT
    const userId = charge.metadata?.user_id;
    const userEmail = charge.metadata?.user_email;
    const userName = charge.metadata?.user_name;

    if (!userId || !userEmail) {
      throw new Error("Missing user metadata in charge");
    }

    console.log(`🎯 Génération rapport pour ${userName} (${userEmail})`);

    // 2. ENREGISTRER LE PAIEMENT EN DB (optional)
    const { error: paymentError } = await supabase
      .from("payments")
      .insert({
        user_id: userId,
        stripe_charge_id: charge.id,
        amount: charge.amount,
        currency: charge.currency,
        status: "succeeded",
      });

    if (paymentError) {
      console.warn("⚠️ Erreur enregistrement paiement:", paymentError);
    }

    // 3. CRÉER UN ENREGISTREMENT "RAPPORT EN COURS" EN DB
    const { data: report, error: reportInsertError } = await supabase
      .from("reports")
      .insert({
        user_id: userId,
        status: "processing",
        initiated_at: new Date().toISOString(),
      })
      .select()
      .single();

    if (reportInsertError) {
      throw new Error(`Erreur création rapport: ${reportInsertError.message}`);
    }

    console.log(`📝 Rapport créé en DB avec statut 'processing'`);

    // 4. DÉCLENCHER L'EDGE FUNCTION SUPABASE
    // L'Edge Function va :
    // - Récupérer les données utilisateur
    // - Appeler OpenAI pour générer le contenu
    // - Générer le PDF
    // - Envoyer l'email

    const triggerResponse = await fetch(
      `${SUPABASE_FUNCTION_URL}/generate-report`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${process.env.SUPABASE_SERVICE_KEY}`,
        },
        body: JSON.stringify({
          user_id: userId,
          user_email: userEmail,
          user_name: userName,
          charge_id: charge.id,
          report_id: report.id,
        }),
      }
    );

    if (!triggerResponse.ok) {
      const errorText = await triggerResponse.text();
      console.error(
        "❌ Erreur appel Edge Function:",
        triggerResponse.status,
        errorText
      );
      
      // Marquer le rapport comme failed, mais ne pas lever l'erreur
      // (pour ne pas rejeter le webhook)
      await supabase
        .from("reports")
        .update({ status: "failed", error: "Edge Function error" })
        .eq("id", report.id);
      
      return;
    }

    const result = await triggerResponse.json();
    console.log("✅ Edge Function déclenchée avec succès");

    // Note: L'Edge Function met à jour elle-même le statut du rapport
    // On n'attend pas ici car c'est asynchrone

  } catch (error) {
    console.error("❌ Erreur handleChargeSucceeded:", error);
    // ⚠️ IMPORTANT: Ne pas lever l'erreur ici car le webhook doit retourner 200
    // Sinon Stripe va réessayer indéfiniment
  }
}

/**
 * HANDLER: Paiement échoué
 */
async function handleChargeFailed(charge: Stripe.Charge) {
  console.log(`❌ Charge failed: ${charge.id}`);

  const userId = charge.metadata?.user_id;

  if (userId) {
    await supabase
      .from("payments")
      .insert({
        user_id: userId,
        stripe_charge_id: charge.id,
        amount: charge.amount,
        currency: charge.currency,
        status: "failed",
        error: charge.failure_message,
      });
  }
}
