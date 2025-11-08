# 🎯 Architecture: Remplacer Make.com par ta Stack Native

## 📊 Vue d'ensemble du flux

```
1. Utilisateur paye 39€ (Stripe)
        ↓
2. Webhook Stripe → pages/api/webhooks/stripe.ts
        ↓
3. Edge Function Supabase: /functions/generate-report
        ↓
4. OpenAI génère le contenu HTML du rapport
        ↓
5. html2pdf.app convertit HTML → PDF
        ↓
6. Supabase Storage: Upload PDF
        ↓
7. Resend: Email avec lien téléchargement
        ↓
8. React Hook: useReportGeneration() informe l'UI
```

---

## 🔧 LES 3 FICHIERS À CRÉER

### FILE 1: `/supabase/functions/generate-report/index.ts`
**Rôle:** Edge Function serverless (remplace Make.com entièrement)
**Quand:** Déclenché après paiement Stripe réussi
**Fait:**
- Récupère les données utilisateur (profil, colorimétrie, morphologie)
- Appelle OpenAI pour générer le contenu
- Génère le PDF
- Upload sur Supabase Storage
- Envoie l'email
- Met à jour le statut en DB

**Avantages vs Make:**
- ✅ Exécution en ~2-3 min (vs 5-10 min Make)
- ✅ Coûts réduits (API OpenAI direct = moins cher)
- ✅ Logs détaillés dans Supabase
- ✅ Pas de limite de scénarios (Make: 5 appels/mois gratuit)

---

### FILE 2: `/src/hooks/useReportGeneration.ts`
**Rôle:** Hook React pour l'interface utilisateur
**Où:** Pages de paiement, dashboard, page "Votre rapport"
**Fait:**
- Démarre la génération après paiement
- Informe l'UI du statut (génération en cours, 30%, 60%, etc.)
- Fournit le lien de téléchargement
- Gère les erreurs

**Usage côté React:**
```tsx
function PaymentSuccess() {
  const { status, reportUrl, startGeneration, downloadReport } = useReportGeneration();
  
  useEffect(() => {
    startGeneration(paymentIntentId);
  }, [paymentIntentId]);

  return (
    <div>
      {status.step === "generating" && (
        <ProgressBar progress={status.progress} />
      )}
      {status.step === "completed" && (
        <button onClick={downloadReport}>📥 Télécharger</button>
      )}
    </div>
  );
}
```

---

### FILE 3: `/pages/api/webhooks/stripe.ts`
**Rôle:** Webhook Stripe (remplace le "Déclencher scénario Make" dans Stripe)
**Quand:** Stripe envoie l'événement `charge.succeeded`
**Fait:**
- Vérifie la signature Stripe
- Extrait les métadonnées du paiement
- Enregistre le paiement en DB
- **Déclenche l'Edge Function**

**Avantages vs Make webhook:**
- ✅ Intégré dans ta stack (pas d'outil externe)
- ✅ Logs dans Vercel/Supabase
- ✅ Possibilité de retry/fallback automatique

---

## 🔗 FLUX TECHNIQUE DÉTAILLÉ

### ÉTAPE 1: Configuration Stripe (AVANT)

```typescript
// Quand tu crées une intention de paiement
const paymentIntent = await stripe.paymentIntents.create({
  amount: 3900, // 39€
  currency: "eur",
  metadata: {
    user_id: "user_123",
    user_email: "jane@example.com",
    user_name: "Jane Doe",
  },
  // ⚠️ À SUPPRIMER: l'événement "charge.succeeded" remplace Make
});
```

### ÉTAPE 2: Webhook Stripe reçoit l'événement

```bash
Stripe → POST https://mystylist.io/api/webhooks/stripe
Headers: stripe-signature: t=1234567890,v1=xxxxx

Body:
{
  "type": "charge.succeeded",
  "data": {
    "object": {
      "id": "ch_1234567890",
      "amount": 3900,
      "metadata": {
        "user_id": "user_123",
        "user_email": "jane@example.com",
        "user_name": "Jane Doe"
      }
    }
  }
}
```

### ÉTAPE 3: `/pages/api/webhooks/stripe.ts` traite l'événement

```typescript
// ✅ Valide la signature
const event = stripe.webhooks.constructEvent(...);

// ✅ Extrait les infos
const { user_id, user_email, user_name } = charge.metadata;

// ✅ Crée le rapport en DB (statut "processing")
const { data: report } = await supabase
  .from("reports")
  .insert({ user_id, status: "processing" });

// ✅ Déclenche l'Edge Function
fetch(`${SUPABASE_FUNCTION_URL}/generate-report`, {
  method: "POST",
  body: JSON.stringify({ user_id, user_email, user_name, report_id })
});

// ✅ Retourne 200 à Stripe
res.status(200).json({ received: true });
```

### ÉTAPE 4: Edge Function `/functions/generate-report/index.ts` exécute

```typescript
// 1️⃣ Récupère les données du profil
const { data: userProfile } = await supabase
  .from("user_profiles")
  .select("colorimetry, morphology, photos")
  .eq("id", userId);

// 2️⃣ Appelle OpenAI pour générer le contenu
const htmlContent = await fetch("https://api.openai.com/v1/chat/completions", {
  // Génère HTML pur du rapport
});

// 3️⃣ Convertit en PDF
const pdfBuffer = await fetch("https://api.html2pdf.app/v1/generate", {
  // HTML → PDF
});

// 4️⃣ Upload le PDF
const { data: upload } = await supabase.storage
  .from("stylist-reports")
  .upload(`reports/${userId}_${Date.now()}.pdf`, pdfBuffer);

// 5️⃣ Met à jour le rapport (statut "completed")
await supabase
  .from("reports")
  .update({
    status: "completed",
    file_path: upload.path,
    public_url: publicUrl
  })
  .eq("id", reportId);

// 6️⃣ Envoie l'email avec le lien
await fetch("https://api.resend.com/emails", {
  body: JSON.stringify({
    to: userEmail,
    html: `<a href="${publicUrl}">Télécharger</a>`
  })
});
```

### ÉTAPE 5: React Hook affiche la progression

```typescript
// useReportGeneration.ts

useEffect(() => {
  // Poll toutes les 5s pour vérifier si le rapport est prêt
  const interval = setInterval(async () => {
    const { data: report } = await supabase
      .from("reports")
      .select("status, public_url")
      .eq("user_id", userId)
      .order("generated_at", { ascending: false })
      .limit(1);
    
    if (report.status === "completed") {
      setReportUrl(report.public_url);
      setStatus({ step: "completed", progress: 100 });
      clearInterval(interval);
    }
  }, 5000);
}, []);
```

---

## 📁 STRUCTURE DE FICHIERS

```
src/
├── hooks/
│   └── useReportGeneration.ts          ← FILE 2
├── pages/
│   ├── api/
│   │   └── webhooks/
│   │       └── stripe.ts                ← FILE 3
│   └── payment-success.tsx
supabase/
└── functions/
    └── generate-report/
        └── index.ts                     ← FILE 1
```

---

## ⚙️ VARIABLES D'ENVIRONNEMENT À CONFIGURER

### `.env.local` (Frontend/Backend)
```bash
# Stripe
NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_live_xxx
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx
SUPABASE_SERVICE_ROLE_KEY=eyJxxx  # ⚠️ Secret!

# OpenAI
OPENAI_API_KEY=sk-xxx

# HTML to PDF
HTML_TO_PDF_API_KEY=xxx

# Resend (emails)
RESEND_API_KEY=re_xxx

# URLs
SUPABASE_FUNCTION_URL=https://xxx.supabase.co/functions/v1
```

### Supabase Secrets (Edge Function)
Deno peut accéder aux variables d'env via `Deno.env.get()`:
```bash
supabase secrets set OPENAI_API_KEY sk-xxx
supabase secrets set HTML_TO_PDF_API_KEY xxx
supabase secrets set RESEND_API_KEY re_xxx
```

---

## 🚀 DÉPLOIEMENT ÉTAPE PAR ÉTAPE

### 1️⃣ Déployer l'Edge Function

```bash
# Login Supabase
supabase login

# Deploy function
supabase functions deploy generate-report

# Vérifier les logs
supabase functions list
supabase functions logs generate-report
```

### 2️⃣ Configurer le Webhook Stripe

```bash
# Aller sur https://dashboard.stripe.com/webhooks

# Créer nouveau endpoint
URL: https://mystylist.io/api/webhooks/stripe
Events: charge.succeeded, charge.failed

# Copier le webhook secret → STRIPE_WEBHOOK_SECRET
```

### 3️⃣ Déployer le code (Vercel)

```bash
git push origin main
# Vercel déploie automatiquement
```

### 4️⃣ Tester

```bash
# Paiement test Stripe
# Utiliser la carte 4242 4242 4242 4242

# Vérifier:
# 1. Webhook reçu: Stripe → Logs de l'endpoint
# 2. Edge Function exécutée: Supabase → Functions → Logs
# 3. Rapport généré: Supabase Storage → stylist-reports
# 4. Email envoyé: Resend → Logs
# 5. React UI mise à jour
```

---

## 🔄 COMPARAISON: Make vs Stack Native

| Aspect | Make.com | Stack Native |
|--------|----------|--------------|
| **Coût** | €0 (gratuit 5/mois), puis €20-100/mois | €0 (Supabase Edge free 10K req/mois) |
| **Latence** | 5-10 min | 1-3 min |
| **Contrôle** | Limité (GUI) | Total (code) |
| **Maintenance** | Dépend de Make | Dépend de toi |
| **Logs** | Limités | Complets dans Supabase |
| **Scaling** | Payant | Gratuit jusqu'à 10K/mois |
| **Intégration custom** | Difficile | Facile |

---

## ⚠️ POINTS D'ATTENTION

### 1️⃣ Timeout Edge Function
- Supabase: Max 600s (10 min) pour Edge Functions
- La génération PDF peut prendre 2-3 min
- ✅ Pas de problème: 2-3 min < 10 min

### 2️⃣ Rate Limiting OpenAI
- Limit: 3,500 RPM
- Avec 50 rapports/mois: ~0.1 RPM
- ✅ Pas de problème

### 3️⃣ Coûts OpenAI
- ~0.05€ par rapport (GPT-4)
- Avec 50 rapports: ~2.50€/mois
- ✅ Très acceptable

### 4️⃣ Webhook Retry Stripe
- Si l'Edge Function échoue, Stripe réessaye 5 fois
- ✅ Confiance accrue: aucun rapport perdu

---

## 📋 CHECKLIST DE MISE EN PLACE

- [ ] Créer `/supabase/functions/generate-report/index.ts`
- [ ] Créer `/src/hooks/useReportGeneration.ts`
- [ ] Créer `/pages/api/webhooks/stripe.ts`
- [ ] Configurer variables d'env (Vercel + Supabase)
- [ ] Déployer Edge Function (`supabase functions deploy`)
- [ ] Configurer webhook Stripe
- [ ] Tester avec paiement test
- [ ] Vérifier logs Supabase + Stripe + Resend
- [ ] Intégrer le hook dans la page PaymentSuccess
- [ ] Vérifier le PDF généré
- [ ] Vérifier l'email reçu

---

## 🆘 DÉPANNAGE

### ❌ Edge Function timeout
```
Solution: Réduire la verbosité du prompt OpenAI
- max_tokens: 4000 → 3000
- Enlever les sections non essentielles
```

### ❌ PDF vide ou mal formaté
```
Solution: Nettoyer le HTML généré par OpenAI
- Supprimer balises markdown
- Vérifier que le HTML est valide
```

### ❌ Email non reçu
```
Solution: Vérifier Resend logs
- Vérifier adresse "from"
- Vérifier AUTH du domaine (SPF/DKIM)
```

### ❌ Rapport non généré (polling timeout)
```
Solution: Vérifier les logs de l'Edge Function
- Supabase → Functions → generate-report → Recent Invocations
- Chercher les erreurs de permissions/API
```

---

## 📞 SUPPORT

Si tu bloques sur un truc:
1. Vérifie les logs Supabase Functions
2. Vérifie les logs Stripe Webhook
3. Teste avec `curl` ou Postman
4. Ajoute des `console.log()` partout

Good luck! 🚀
