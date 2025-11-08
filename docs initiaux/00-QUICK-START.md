# ⚡ QUICK START: Remplacer Make.com en 5 étapes

## 🎯 TL;DR
Tu veux remplacer le scénario Make.com qui génère le rapport après paiement Stripe.
Au lieu d'utiliser Make, tu vas utiliser ta propre stack: Supabase + React + Next.js

**Résultat:** Même fonctionnalité, mais 3x plus rapide et moins cher.

---

## 📦 LES 3 FICHIERS À CRÉER

| Fichier | Rôle | Où |
|---------|------|-----|
| `supabase/functions/generate-report/index.ts` | Génère le PDF (remplace Make) | Supabase Edge Function |
| `src/hooks/useReportGeneration.ts` | UI progression (affiche "Génération en cours...") | React Hook |
| `pages/api/webhooks/stripe.ts` | Déclenche la génération (reçoit webhook Stripe) | Next.js API Route |

---

## 🚀 DÉMARRAGE RAPIDE (10 MIN)

### Étape 1: Copier les 3 fichiers
```bash
# Voir les 4 fichiers dans /outputs:
# - 01-supabase-edge-function-generate-report.ts → supabase/functions/generate-report/index.ts
# - 02-useReportGeneration-hook.ts → src/hooks/useReportGeneration.ts
# - 03-stripe-webhook-api-route.ts → pages/api/webhooks/stripe.ts
# - 04-payment-success-page-example.tsx → pages/payment-success.tsx (exemple)
```

### Étape 2: Configurer les variables d'env
```bash
# Ajouter à .env.local:
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJxxx
OPENAI_API_KEY=sk-xxx
RESEND_API_KEY=re_xxx
HTML_TO_PDF_API_KEY=xxx

# Ajouter aussi sur Vercel: Settings → Environment Variables
```

### Étape 3: Déployer l'Edge Function
```bash
supabase functions deploy generate-report
```

### Étape 4: Configurer webhook Stripe
```bash
# https://dashboard.stripe.com/webhooks
# Créer endpoint: https://mystylist.io/api/webhooks/stripe
# Events: charge.succeeded, charge.failed
# Copier webhook secret → STRIPE_WEBHOOK_SECRET
```

### Étape 5: Déployer sur Vercel
```bash
git push origin main
# Vercel déploie automatiquement
```

---

## ✅ TESTER

```bash
# 1. Utiliser une carte test Stripe: 4242 4242 4242 4242

# 2. Faire un paiement

# 3. Vérifier:
# - Logs Supabase: supabase functions logs generate-report
# - Logs Vercel: https://vercel.com/dashboard
# - Storage: PDF uploadé sur Supabase
# - Email: Reçu dans ta boîte
# - UI: Page affiche "Rapport généré!" 🎉
```

---

## 💰 ÉCONOMIES

| Aspect | Make | Stack Native |
|--------|------|--------------|
| Coût/mois | €20-100 | €0 (gratuit 10K) |
| Temps génération | 5-10 min | 1-3 min |
| Coût/rapport | ~€0.40 | ~€0.05 |

**Avec 50 rapports/mois:**
- Make: ~50€/mois
- Stack Native: €2.50/mois (OpenAI seulement)

**Économie: 47.50€/mois 💰**

---

## 🔧 SI QUELQUE CHOSE NE MARCHE PAS

### Webhook Stripe ne reçoit pas
```bash
# Utiliser Stripe CLI pour tester localement
stripe listen --forward-to localhost:3000/api/webhooks/stripe
stripe trigger charge.succeeded
```

### Edge Function timeout
```
# Réduire max_tokens: 4000 → 3000 dans le prompt OpenAI
# Ou utiliser GPT-3.5-turbo au lieu de GPT-4
```

### PDF vide
```
# Vérifier que le HTML généré est valide (pas de backticks)
# Ajouter console.log(htmlContent) dans l'Edge Function
```

### Email non reçu
```
# Vérifier Resend: https://resend.com/emails
# S'assurer que le domaine est validé (SPF/DKIM)
```

---

## 📋 STRUCTURE FINALE

```
mystylist.io/
├── supabase/
│   └── functions/
│       └── generate-report/
│           └── index.ts                    ← FILE 1
├── src/
│   └── hooks/
│       └── useReportGeneration.ts           ← FILE 2
└── pages/
    ├── api/
    │   └── webhooks/
    │       └── stripe.ts                    ← FILE 3
    ├── payment-success.tsx                 ← FILE 4 (exemple)
    └── ...
```

---

## 🎁 BONUS: AMÉLIORATIONS FUTURES

Après que ça marche:
- [ ] Ajouter cache (ne pas regénérer si déjà généré)
- [ ] Intégrer les images (produits réels dans le PDF)
- [ ] Personnaliser davantage le contenu
- [ ] Ajouter signatures/options de paiement alternatives

---

## 📞 BESOIN D'AIDE?

1. Vérifie les logs: `supabase functions logs generate-report`
2. Consulte la checklist détaillée: `05-DETAILED-CHECKLIST-SETUP.md`
3. Voir l'architecture complète: `README-ARCHITECTURE-SETUP.md`

**C'est tout! Tu peux maintenant lancer la génération de rapports nativement. 🚀**
