"""
OpenAI Call Tracker v2.0 - Orchestration complète des logs
✅ S'intègre avec token_counter.py existant
✅ Track chaque appel: prompt/completion tokens, réponses, erreurs
✅ Résumé final clair par section (Colorimetry, Morphology, Styling)
✅ Affiche les bugs et erreurs clairement
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class APICall:
    """Représente un appel API OpenAI"""
    section: str  # "Colorimetry", "Morphology", "Styling"
    subsection: str  # "Part 1", "Part 2", "Part 3", ou vide
    service: str  # "colorimetry_service", "morphology_service", "styling_service"
    
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    budget_percent: float = 0.0
    
    raw_response_preview: str = ""
    parse_success: bool = False
    parse_error: str = ""
    
    response_timestamp: Optional[str] = None
    duration_seconds: float = 0.0
    
    def get_status_emoji(self) -> str:
        """Retourne emoji de status"""
        if self.parse_success:
            return "✅"
        else:
            return "❌"
    
    def get_budget_status(self) -> str:
        """Retourne status du budget"""
        if self.budget_percent > 100:
            return "❌ OVER"
        elif self.budget_percent > 90:
            return "⚠️  WARN"
        else:
            return "✅ OK"


class CallTracker:
    """
    Tracker central pour tous les appels OpenAI
    Orchestre les logs et affiche un résumé final
    """
    
    def __init__(self, budget_total: int = 4000):
        self.budget_total = budget_total
        self.calls: List[APICall] = []
        self.start_time = datetime.now()
        self.errors: List[str] = []
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # LOGGING D'UN APPEL
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def log_api_call(
        self,
        section: str,
        subsection: str,
        service: str,
        prompt_tokens: int,
        completion_tokens: int,
        raw_response_preview: str = "",
        parse_success: bool = True,
        parse_error: str = ""
    ) -> APICall:
        """
        Log un appel OpenAI complètement
        
        Args:
            section: "Colorimetry", "Morphology", "Styling"
            subsection: "Part 1", "Part 2", "Part 3", ou ""
            service: nom du service
            prompt_tokens: tokens du prompt
            completion_tokens: tokens de la réponse
            raw_response_preview: premiers chars de la réponse
            parse_success: si le parsing JSON a réussi
            parse_error: message d'erreur si parsing échoué
        
        Returns:
            APICall tracké
        """
        total = prompt_tokens + completion_tokens
        budget_percent = (total / self.budget_total) * 100
        
        call = APICall(
            section=section,
            subsection=subsection,
            service=service,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            budget_percent=budget_percent,
            raw_response_preview=raw_response_preview,
            parse_success=parse_success,
            parse_error=parse_error,
            response_timestamp=datetime.now().isoformat()
        )
        
        self.calls.append(call)
        
        # Afficher le log structuré
        self._print_call_log(call)
        
        return call
    
    def _print_call_log(self, call: APICall):
        """Affiche un log structuré pour un appel"""
        print(f"\n{'='*80}")
        
        # Titre avec section et subsection
        title = f"{call.section}"
        if call.subsection:
            title += f" - {call.subsection}"
        print(f"📊 {title}")
        print(f"{'='*80}\n")
        
        # Tokens
        print(f"📝 TOKENS CONSOMMÉS:")
        print(f"   • Prompt: {call.prompt_tokens}")
        print(f"   • Completion: {call.completion_tokens}")
        print(f"   • Total: {call.total_tokens}")
        print(f"   • Budget: {call.budget_percent:.1f}% ({call.total_tokens}/{self.budget_total})")
        print(f"   • Status: {call.get_budget_status()}\n")
        
        # Réponse brute
        if call.raw_response_preview:
            print(f"📨 RÉPONSE BRUTE (premiers 150 chars):")
            print(f"   {call.raw_response_preview[:150]}...\n")
        
        # Parsing
        print(f"🔍 PARSING:")
        if call.parse_success:
            print(f"   {call.get_status_emoji()} Succès\n")
        else:
            print(f"   {call.get_status_emoji()} Erreur: {call.parse_error}\n")
    
    def log_error(self, section: str, error_msg: str, traceback_preview: str = ""):
        """Log une erreur dans une section"""
        error_full = f"[{section}] {error_msg}"
        if traceback_preview:
            error_full += f"\n   {traceback_preview[:200]}"
        
        self.errors.append(error_full)
        print(f"\n❌ ERREUR: {error_full}\n")
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # RÉSUMÉ FINAL
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def print_summary(self):
        """Affiche un résumé final complet de tous les appels"""
        if not self.calls:
            print("\n⚠️ Aucun appel tracké")
            return
        
        print("\n\n" + "="*80)
        print("🎯 RÉSUMÉ FINAL - TOUS LES APPELS OPENAI")
        print("="*80 + "\n")
        
        # Grouper par section
        sections = {}
        for call in self.calls:
            if call.section not in sections:
                sections[call.section] = []
            sections[call.section].append(call)
        
        # Afficher par section
        total_tokens = 0
        total_calls = 0
        total_success = 0
        
        for section_name in ["Colorimetry", "Morphology", "Styling"]:
            if section_name not in sections:
                continue
            
            calls = sections[section_name]
            section_tokens = sum(c.total_tokens for c in calls)
            section_success = sum(1 for c in calls if c.parse_success)
            
            total_tokens += section_tokens
            total_calls += len(calls)
            total_success += section_success
            
            print(f"📌 {section_name.upper()}")
            print(f"   Appels: {len(calls)}")
            
            # Si plusieurs appels (Part 1, 2, 3), afficher chacun
            if len(calls) > 1:
                for call in calls:
                    subsec = f" - {call.subsection}" if call.subsection else ""
                    status = call.get_status_emoji()
                    print(f"      {status} {call.subsection or 'Appel'}: {call.total_tokens} tokens ({call.budget_percent:.1f}%)")
            else:
                # Un seul appel
                call = calls[0]
                status = call.get_status_emoji()
                print(f"      {status} {call.total_tokens} tokens ({call.budget_percent:.1f}%)")
            
            print(f"   Subtotal: {section_tokens} tokens")
            print(f"   Succès: {section_success}/{len(calls)}\n")
        
        # Grand total
        print(f"{'-'*80}")
        global_budget_percent = (total_tokens / self.budget_total) * 100
        print(f"TOTAL: {total_tokens} tokens / {self.budget_total} ({global_budget_percent:.1f}%)")
        print(f"Appels: {total_success}/{total_calls} réussis")
        
        if global_budget_percent > 100:
            print(f"❌ DÉPASSEMENT DE {global_budget_percent - 100:.1f}%!")
        elif global_budget_percent > 90:
            print(f"⚠️  Approche de la limite!")
        else:
            remaining = self.budget_total - total_tokens
            print(f"✅ OK - {remaining} tokens restants")
        
        print("="*80 + "\n")
        
        # Afficher les erreurs si y en a
        if self.errors:
            print(f"\n❌ ERREURS RENCONTRÉES:\n")
            for error in self.errors:
                print(f"   {error}\n")
    
    def get_summary_dict(self) -> Dict[str, Any]:
        """Retourne un dict avec résumé pour tracking/analytics"""
        sections = {}
        total_tokens = 0
        total_success = 0
        
        for call in self.calls:
            if call.section not in sections:
                sections[call.section] = {
                    "calls": [],
                    "total_tokens": 0,
                    "success_count": 0
                }
            
            sections[call.section]["calls"].append({
                "subsection": call.subsection,
                "tokens": call.total_tokens,
                "success": call.parse_success,
                "budget_percent": call.budget_percent
            })
            sections[call.section]["total_tokens"] += call.total_tokens
            if call.parse_success:
                sections[call.section]["success_count"] += 1
            
            total_tokens += call.total_tokens
            if call.parse_success:
                total_success += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_calls": len(self.calls),
            "total_tokens": total_tokens,
            "budget_percent": (total_tokens / self.budget_total) * 100,
            "total_success": total_success,
            "sections": sections,
            "errors": self.errors
        }


# Instance globale
call_tracker = CallTracker(budget_total=4000)