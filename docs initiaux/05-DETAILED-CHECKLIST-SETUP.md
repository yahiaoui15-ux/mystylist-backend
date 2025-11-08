# 📋 CHECKLIST COMPLÈTE: DE MAKE À STACK NATIVE

## 🎯 OBJECTIF
Remplacer le scénario Make.com (après paiement Stripe) par 3 fichiers:
1. Edge Function Supabase (génération du rapport)
2. Hook React (UI progression)
3. Webhook API (déclenchement)

---

## PHASE 1: PRÉPARATION

### 1.1 Vérifier les accès et clés

- [ ] Compte Supabase actif
  ```bash
  # Vérifier
  supabase projects list
  ```

- [ ] Compte Stripe avec webhooks
  - [ ] Aller sur https://dashboard.stripe.com/webhooks
  - [ ] Noter la **webhook secret** (whsec_...)

- [ ] Compte OpenAI avec API key
  - [ ] https://platform.openai.com/account/api-keys
  - [ ] Créer une clé (sk-...)

- [ ] Compte Resend (emails)
  - [ ] https://resend.com
  - [ ] API key (re_...)

- [ ] Service HTML to PDF (optionnel)
  - [ ] https://html2pdf.app
  - [ ] API key

### 1.2 Configurer les variables d'environnement

#### Dans `.env.local` (repo local)
```bash
# Stripe
NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_live_xxx
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx
SUPABASE_SERVICE_ROLE_KEY=eyJxxx

# OpenAI
OPENAI_API_KEY=sk-xxx

# HTML to PDF
HTML_TO_PDF_API_KEY=xxx

# Resend
RESEND_API_KEY=re_xxx

# Supabase Function URL
SUPABASE_FUNCTION_URL=https://xxxyyyzzz.supabase.co/functions/v1
```

#### Sur Vercel (production)
```bash
# Aller sur https://vercel.com/dashboard
# Settings → Environment Variables
# Ajouter toutes les variables ci-dessus
```

#### Sur Supabase (Edge Function secrets)
```bash
# CLI
supabase secrets set OPENAI_API_KEY sk-xxx
supabase secrets set RESEND_API_KEY re_xxx
supabase secrets set HTML_TO_PDF_API_KEY xxx

# Vérifier
supabase secrets list
```

---

## PHASE 2: CRÉER LES FICHIERS

### 2.1 Créer l'Edge Function

**Fichier:** `supabase/functions/generate-report/index.ts`

```bash
# Créer le dossier
mkdir -p supabase/functions/generate-report

# Copier le contenu du FILE 1 dans index.ts
# (voir: 01-supabase-edge-function-generate-report.ts)
```

**Tester localement:**
```bash
# Lancer le serveur de développement Supabase
supabase start

# Dans un autre terminal, tester la function
curl -X POST http://localhost:54321/functions/v1/generate-report \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{"user_id":"test_user"}'
```

### 2.2 Créer le Hook React

**Fichier:** `src/hooks/useReportGeneration.ts`

```bash
# Créer le dossier
mkdir -p src/hooks

# Copier le contenu du FILE 2 dans useReportGeneration.ts
# (voir: 02-useReportGeneration-hook.ts)
```

**Tester:**
```bash
# Juste une vérification syntaxe
npm run build
```

### 2.3 Créer le Webhook Stripe

**Fichier:** `pages/api/webhooks/stripe.ts`

```bash
# Créer le dossier
mkdir -p pages/api/webhooks

# Copier le contenu du FILE 3 dans stripe.ts
# (voir: 03-stripe-webhook-api-route.ts)
```

**Tester:**
```bash
# Lancer le serveur dev
npm run dev

# Le webhook sera accessible sur:
# http://localhost:3000/api/webhooks/stripe
```

### 2.4 Créer la page PaymentSuccess

**Fichier:** `pages/payment-success.tsx`

```bash
# Copier le contenu du FILE 4
# (voir: 04-payment-success-page-example.tsx)
```

---

## PHASE 3: CONFIGURER LES WEBHOOKS

### 3.1 Configurer Stripe Webhook

```bash
# 1. Aller sur https://dashboard.stripe.com/webhooks

# 2. Créer un nouvel endpoint:
#    URL: https://VOTRE_DOMAINE.com/api/webhooks/stripe
#    
#    Exemple (production):
#    https://mystylist.io/api/webhooks/stripe
#    
#    Exemple (développement local):
#    https://xxx.ngrok.io/api/webhooks/stripe  (avec ngrok)

# 3. Sélectionner les événements:
#    ✓ charge.succeeded
#    ✓ charge.failed

# 4. Créer l'endpoint

# 5. Copier la "Signing Secret" (whsec_...)
#    → Ajouter à STRIPE_WEBHOOK_SECRET
```

**Tester le webhook localement:**
```bash
# 1. Installer ngrok
# https://ngrok.com/download

# 2. Lancer ngrok
ngrok http 3000

# 3. Copier l'URL générée (https://xxx.ngrok.io)

# 4. Configurer le webhook Stripe sur cette URL

# 5. Lancer le serveur dev
npm run dev

# 6. Faire un paiement test Stripe
# Voir les logs dans la console
```

### 3.2 Tester le webhook avec l'CLI Stripe

```bash
# 1. Installer Stripe CLI
# https://stripe.com/docs/stripe-cli

# 2. Login
stripe login

# 3. Écouter les webhooks localement
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# 4. Copier le webhook secret (whsec_...)
#    → Ajouter à STRIPE_WEBHOOK_SECRET

# 5. Déclencher un événement test
stripe trigger charge.succeeded

# 6. Vérifier les logs du serveur
```

---

## PHASE 4: DÉPLOYER

### 4.1 Déployer l'Edge Function

```bash
# 1. S'assurer qu'on est dans le bon projet
supabase projects list

# 2. Déployer
supabase functions deploy generate-report

# 3. Vérifier le déploiement
supabase functions list

# 4. Voir les logs
supabase functions logs generate-report

# 5. Tester la function en production
curl -X POST https://xxxyyyzzz.supabase.co/functions/v1/generate-report \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -d '{"user_id":"test_user"}'
```

### 4.2 Déployer sur Vercel

```bash
# 1. Push le code
git add .
git commit -m "feat: replace Make.com with native stack for report generation"
git push origin main

# 2. Vercel déploie automatiquement

# 3. Vérifier les logs
# https://vercel.com/dashboard → Logs

# 4. Tester l'API webhook
curl -X POST https://mystylist.io/api/webhooks/stripe \
  -H "Content-Type: application/json" \
  -H "stripe-signature: t=1234567890,v1=xxxxx" \
  -d '{...}'
```

### 4.3 Mettre à jour la configuration Stripe

```bash
# 1. Aller sur https://dashboard.stripe.com/webhooks

# 2. Mettre à jour l'endpoint:
#    URL: https://mystylist.io/api/webhooks/stripe

# 3. Tester: https://dashboard.stripe.com/webhooks/[webhook_id]
#    → Cliquer "Send test webhook"
```

---

## PHASE 5: TESTER EN PRODUCTION

### 5.1 Paiement test complet

```bash
# 1. Aller sur https://mystylist.io (ta page de paiement)

# 2. Utiliser une carte test Stripe:
#    Numéro: 4242 4242 4242 4242
#    Expiration: 12/25
#    CVC: 123

# 3. Compléter le paiement

# 4. Vérifier:

#    ✓ Stripe: https://dashboard.stripe.com/events
#       Chercher l'événement charge.succeeded

#    ✓ Edge Function: Supabase Dashboard → Functions → Logs
#       Chercher les logs de generate-report

#    ✓ Base de données: Supabase → Editor → reports table
#       Vérifier le nouveau rapport (status: "completed")

#    ✓ Storage: Supabase → Storage → stylist-reports
#       Vérifier le PDF uploadé

#    ✓ Email: Vérifier ta boîte mail
#       Chercher l'email de Resend avec le lien

#    ✓ UI: La page payment-success affiche la progression
#       Après ~3 min, elle affiche le bouton de téléchargement
```

### 5.2 Vérifier les logs

```bash
# Logs Supabase
supabase functions logs generate-report

# Logs Vercel (API webhook)
https://vercel.com/dashboard → Logs

# Logs Stripe
https://dashboard.stripe.com/logs

# Logs Resend (emails)
https://resend.com/emails

# Logs OpenAI (si disponible)
https://platform.openai.com/account/usage
```

---

## PHASE 6: OPTIMISATIONS

### 6.1 Monitorer les erreurs

```bash
# Ajouter Sentry pour les erreurs
npm install @sentry/nextjs

# Config dans sentry.config.js
```

### 6.2 Cacher les résultats

```bash
# Ajouter une table reports_cache pour éviter regénération
# Si même user repaie, utiliser le rapport existant (5 jours max)
```

### 6.3 Améliorer la performance

```bash
# Réduire max_tokens OpenAI: 4000 → 3000 (économise 20% time)
# Utiliser GPT-3.5-turbo pour les sections simples
# Prégenérer certaines sections statiques
```

---

## 🚨 TROUBLESHOOTING

### ❌ Edge Function timeout

**Symptôme:** La fonction prend > 10 min

**Solution:**
```bash
# 1. Réduire le contenu généré
# Dans le prompt OpenAI, réduire max_tokens: 4000 → 3000

# 2. Paralléliser les appels OpenAI
# Générer 3 sections en parallèle au lieu de séquentiellement

# 3. Utiliser un modèle plus rapide
# GPT-4 → GPT-3.5-turbo (génération 2x plus rapide)
```

### ❌ Webhook Stripe ne reçoit pas

**Symptôme:** L'API webhook ne reçoit rien

**Solution:**
```bash
# 1. Vérifier l'URL du webhook
#    https://dashboard.stripe.com/webhooks

# 2. Vérifier les logs d'erreur
#    https://dashboard.stripe.com/webhooks/[id]/logs

# 3. Tester manuellement
curl -X POST https://mystylist.io/api/webhooks/stripe \
  -H "Content-Type: application/json" \
  -d '{"type":"charge.succeeded","data":{"object":{"id":"ch_123"}}}'

# 4. Vérifier que l'API retourne 200
```

### ❌ PDF vide ou mal formaté

**Symptôme:** Le PDF généré est vide ou sans mise en page

**Solution:**
```bash
# 1. Vérifier le HTML généré par OpenAI
#    Ajouter console.log(htmlContent) dans l'Edge Function

# 2. Valider le HTML
#    Passer par https://validator.w3.org

# 3. S'assurer que html2pdf.app reçoit du HTML valide
#    Pas de backticks, pas de balises markdown

# 4. Test local
echo "<h1>Test</h1>" | curl -X POST https://api.html2pdf.app/v1/generate \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: YOUR_KEY" \
  -d '{"html":"<h1>Test</h1>"}'
```

### ❌ Email non reçu

**Symptôme:** Pas d'email après génération

**Solution:**
```bash
# 1. Vérifier Resend logs
#    https://resend.com/emails

# 2. S'assurer que le domaine est configuré
#    SPF, DKIM records valides
#    https://resend.com/domains

# 3. Vérifier que l'adresse "from" est correcte
#    Doit matcher le domaine configuré

# 4. Vérifier RESEND_API_KEY en env
supabase secrets list
```

### ❌ Rapport ne se génère pas (polling timeout)

**Symptôme:** Après 5 min, toujours "en cours de génération"

**Solution:**
```bash
# 1. Vérifier les logs de l'Edge Function
supabase functions logs generate-report

# 2. Vérifier le statut du rapport en DB
SELECT * FROM reports WHERE user_id = 'xxx' ORDER BY created_at DESC LIMIT 1;

# 3. Augmenter le timeout du polling
#    Dans useReportGeneration.ts, passer maxAttempts: 60 → 120

# 4. Vérifier les permissions Supabase
#    Le service_role_key a-t-il accès à "reports" table?
```

---

## ✅ CHECKLIST FINALE

- [ ] Tous les fichiers créés (4 fichiers)
- [ ] Variables d'env configurées (Vercel + Supabase)
- [ ] Edge Function déployée et testée
- [ ] Webhook Stripe créé et pointé sur l'API
- [ ] Paiement test effectué
- [ ] Logs vérifiés (Supabase + Stripe)
- [ ] Rapport généré avec succès
- [ ] Email reçu
- [ ] UI affiche la progression correctement
- [ ] PDF téléchargeable

---

## 📞 SUPPORT

Si quelque chose ne fonctionne pas:
1. Vérifier les logs Supabase Functions
2. Vérifier les logs Vercel
3. Vérifier les logs Stripe Webhooks
4. Ajouter des console.log() partout
5. Utiliser Postman pour tester les APIs

Bon courage! 🚀
