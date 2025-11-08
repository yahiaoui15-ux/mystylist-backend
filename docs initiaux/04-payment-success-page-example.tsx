/**
 * pages/payment-success.tsx
 * 
 * Exemple d'intégration complète du hook useReportGeneration
 * Affiche la progression de génération du rapport après paiement
 */

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useReportGeneration } from "@/hooks/useReportGeneration";

export default function PaymentSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const paymentIntentId = searchParams.get("payment_intent_id");

  const { status, reportUrl, startGeneration, downloadReport, isGenerating } =
    useReportGeneration();

  // Déclencher la génération automatiquement au montage
  useEffect(() => {
    if (paymentIntentId && !isGenerating) {
      startGeneration(paymentIntentId).catch((error) => {
        console.error("Erreur génération rapport:", error);
      });
    }
  }, [paymentIntentId, isGenerating, startGeneration]);

  // Refresh le rapport généré
  const handleRefresh = () => {
    if (paymentIntentId) {
      startGeneration(paymentIntentId);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-20px shadow-2xl p-8 md:p-12">
        {/* HEADER */}
        <div className="text-center mb-12">
          <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-4xl">✨</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            Paiement réussi!
          </h1>
          <p className="text-lg text-gray-600">
            Votre rapport stylistique est en cours de génération...
          </p>
        </div>

        {/* STATUTS POSSIBLES */}

        {/* 1️⃣ EN ATTENTE */}
        {status.step === "waiting" && (
          <div className="text-center py-12">
            <div className="inline-flex flex-col items-center gap-4">
              <div className="w-16 h-16 rounded-full border-4 border-gray-200 flex items-center justify-center">
                <span className="text-2xl">⏳</span>
              </div>
              <p className="text-gray-600">En attente d'initialisation...</p>
            </div>
          </div>
        )}

        {/* 2️⃣ GÉNÉRATION EN COURS */}
        {(status.step === "generating" ||
          status.step === "processing_pdf" ||
          status.step === "uploading" ||
          status.step === "sending_email") && (
          <div className="space-y-8">
            {/* Progress Bar */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <p className="text-lg font-semibold text-gray-900">
                  {status.message}
                </p>
                <span className="text-sm font-bold text-purple-600">
                  {Math.round(status.progress)}%
                </span>
              </div>

              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-full transition-all duration-500 ease-out"
                  style={{ width: `${status.progress}%` }}
                />
              </div>
            </div>

            {/* Étapes */}
            <div className="space-y-3">
              <StepIndicator
                step="Analyse colorimétrique"
                isActive={status.progress > 15}
                isComplete={status.progress > 25}
              />
              <StepIndicator
                step="Analyse morphologique"
                isActive={status.progress > 30}
                isComplete={status.progress > 45}
              />
              <StepIndicator
                step="Génération du rapport"
                isActive={status.progress > 50}
                isComplete={status.progress > 70}
              />
              <StepIndicator
                step="Conversion PDF"
                isActive={status.progress > 75}
                isComplete={status.progress > 85}
              />
              <StepIndicator
                step="Envoi email"
                isActive={status.progress > 85}
                isComplete={status.progress > 95}
              />
            </div>

            {/* Timer */}
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
              <p className="text-sm text-blue-800">
                ℹ️ La génération prend généralement 2-3 minutes. Ne quittez pas cette page.
              </p>
            </div>
          </div>
        )}

        {/* 3️⃣ SUCCÈS */}
        {status.step === "completed" && reportUrl && (
          <div className="space-y-8">
            {/* Checkmark Animation */}
            <div className="flex justify-center">
              <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-12 h-12 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
            </div>

            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Rapport généré avec succès! 🎉
              </h2>
              <p className="text-gray-600 mb-6">
                Votre rapport stylistique est prêt à télécharger. Un email vous a également été envoyé avec le lien.
              </p>
            </div>

            {/* Download Button */}
            <button
              onClick={downloadReport}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 px-6 rounded-lg transition-all duration-200 text-lg flex items-center justify-center gap-3"
            >
              <span>📥</span>
              <span>Télécharger mon rapport (PDF)</span>
            </button>

            {/* Alternative: Direct Link */}
            <a
              href={reportUrl}
              download={`rapport-stylistique-${new Date().toISOString().split("T")[0]}.pdf`}
              className="w-full block text-center bg-gray-100 hover:bg-gray-200 text-gray-900 font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              Ouvrir dans le navigateur
            </a>

            {/* What's Next */}
            <div className="bg-purple-50 border-l-4 border-purple-500 p-4 rounded">
              <h3 className="font-bold text-purple-900 mb-2">Prochaines étapes:</h3>
              <ul className="text-sm text-purple-800 space-y-1">
                <li>✓ Téléchargez et consultez votre rapport</li>
                <li>✓ Découvrez vos palettes de couleurs personnalisées</li>
                <li>✓ Explorez votre garde-robe capsule recommandée</li>
                <li>✓ Trouvez les marques qui vous correspondent</li>
              </ul>
            </div>

            {/* Dashboard Link */}
            <button
              onClick={() => router.push("/dashboard/mon-rapport")}
              className="w-full bg-white border-2 border-gray-300 hover:border-purple-500 text-gray-900 hover:text-purple-600 font-bold py-3 px-6 rounded-lg transition-colors"
            >
              Voir mon rapport dans le dashboard
            </button>
          </div>
        )}

        {/* 4️⃣ ERREUR */}
        {status.step === "error" && (
          <div className="space-y-6">
            <div className="flex justify-center">
              <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center">
                <span className="text-4xl">⚠️</span>
              </div>
            </div>

            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Oups, une erreur s'est produite
              </h2>
              <p className="text-gray-600 mb-4">{status.error}</p>
            </div>

            {/* Error Details */}
            {status.error && (
              <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                <p className="text-sm text-red-800 font-mono">{status.error}</p>
              </div>
            )}

            {/* Retry Button */}
            <button
              onClick={handleRefresh}
              className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-4 px-6 rounded-lg transition-all duration-200"
            >
              🔄 Réessayer
            </button>

            {/* Support */}
            <div className="text-center">
              <p className="text-gray-600 mb-2">Besoin d'aide?</p>
              <a
                href="mailto:support@mystylist.io"
                className="text-purple-600 hover:text-purple-700 font-semibold"
              >
                Contactez le support
              </a>
            </div>
          </div>
        )}

        {/* FOOTER */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <p className="text-center text-sm text-gray-500">
            Problème? Vérifiez vos emails (spam inclus). Vous recevrez un lien de téléchargement.
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Composant Step Indicator
 */
function StepIndicator({
  step,
  isActive,
  isComplete,
}: {
  step: string;
  isActive: boolean;
  isComplete: boolean;
}) {
  return (
    <div className="flex items-center gap-3">
      <div
        className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-sm transition-all ${
          isComplete
            ? "bg-green-500 text-white"
            : isActive
              ? "bg-purple-500 text-white animate-pulse"
              : "bg-gray-300 text-gray-600"
        }`}
      >
        {isComplete ? "✓" : "•"}
      </div>
      <span
        className={`text-sm font-medium transition-colors ${
          isComplete || isActive ? "text-gray-900" : "text-gray-500"
        }`}
      >
        {step}
      </span>
    </div>
  );
}
