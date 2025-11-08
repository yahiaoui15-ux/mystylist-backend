/**
 * useReportGeneration.ts
 * 
 * Hook React pour gérer la génération du rapport après paiement Stripe
 * À placer: src/hooks/useReportGeneration.ts
 * 
 * Remplace le déclenchement manuel du scénario Make dans Stripe
 */

import { useState, useCallback } from "react";
import { useAuthContext } from "@/contexts/AuthContext";
import { supabase } from "@/lib/supabase";

interface GenerationStatus {
  step: "waiting" | "generating" | "processing_pdf" | "uploading" | "sending_email" | "completed" | "error";
  progress: number; // 0-100
  message: string;
  error?: string;
}

export function useReportGeneration() {
  const { user } = useAuthContext();
  const [status, setStatus] = useState<GenerationStatus>({
    step: "waiting",
    progress: 0,
    message: "",
  });
  const [reportUrl, setReportUrl] = useState<string | null>(null);

  /**
   * 1. DÉCLENCHER LA GÉNÉRATION (côté client)
   * Appelé automatiquement après paiement Stripe réussi
   */
  const startGeneration = useCallback(
    async (paymentIntentId: string) => {
      if (!user) {
        setStatus({
          step: "error",
          progress: 0,
          message: "Utilisateur non authentifié",
          error: "User not authenticated",
        });
        return;
      }

      try {
        setStatus({
          step: "generating",
          progress: 10,
          message: "Initialisation de la génération du rapport...",
        });

        // 2. NOTIFIER L'EDGE FUNCTION VIA WEBHOOK STRIPE
        // Le webhook Stripe appellera automatiquement l'Edge Function
        // Mais on peut aussi déclencher manuellement:

        const response = await fetch("/api/trigger-report-generation", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: user.id,
            payment_intent_id: paymentIntentId,
          }),
        });

        if (!response.ok) {
          throw new Error("Erreur déclenchement génération");
        }

        setStatus({
          step: "processing_pdf",
          progress: 30,
          message: "Génération du rapport en cours (2-3 min)...",
        });

        // 3. POLL LE STATUT DE GÉNÉRATION
        // Vérifier toutes les 5 secondes si le rapport est prêt
        let reportData = null;
        let attempts = 0;
        const maxAttempts = 60; // 5 min de polling

        while (!reportData && attempts < maxAttempts) {
          await new Promise((resolve) => setTimeout(resolve, 5000)); // Attendre 5s

          const { data, error } = await supabase
            .from("reports")
            .select("*")
            .eq("user_id", user.id)
            .order("generated_at", { ascending: false })
            .limit(1)
            .single();

          if (data && data.status === "completed") {
            reportData = data;
            break;
          }

          attempts++;
          const progress = 30 + (attempts / maxAttempts) * 60;
          setStatus({
            step: "processing_pdf",
            progress,
            message: `Rapport en cours de génération... (${attempts * 5}s)`,
          });
        }

        if (!reportData) {
          throw new Error("Timeout: rapport non généré après 5 min");
        }

        setStatus({
          step: "completed",
          progress: 100,
          message: "Rapport généré avec succès ! 🎉",
        });

        setReportUrl(reportData.public_url);

        // 4. RETOURNER LE LIEN
        return reportData.public_url;
      } catch (error) {
        console.error("❌ Erreur génération rapport:", error);
        setStatus({
          step: "error",
          progress: 0,
          message: "Erreur lors de la génération",
          error: error.message,
        });
        throw error;
      }
    },
    [user]
  );

  /**
   * DOWNLOAD LE RAPPORT
   */
  const downloadReport = useCallback(() => {
    if (!reportUrl) return;

    const link = document.createElement("a");
    link.href = reportUrl;
    link.download = `rapport-stylistique-${new Date().toISOString().split("T")[0]}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }, [reportUrl]);

  return {
    status,
    reportUrl,
    startGeneration,
    downloadReport,
    isGenerating: status.step !== "waiting" && status.step !== "completed" && status.step !== "error",
  };
}
