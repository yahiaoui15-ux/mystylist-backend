"""
Morphology Service v5.2 - FINAL CORRIGÉ
✅ Accepte la vraie structure retournée par Part 1
✅ Génère highlights et minimizes EN INTERNE à partir de body_parts_to_highlight/minimize
✅ Fusionne avec onboarding morphology_goals
✅ Génère explanation et tips enrichis personnalisés
"""

import json
import re
from app.utils.openai_client import openai_client
from app.utils.openai_call_tracker import call_tracker
from app.prompts.morphology_part1_prompt import (
    MORPHOLOGY_PART1_SYSTEM_PROMPT,
    MORPHOLOGY_PART1_USER_PROMPT,
    MORPHOLOGY_PART1_NOPHOTO_USER_PROMPT,
)
from app.prompts.morphology_part2_prompt import MORPHOLOGY_PART2_SYSTEM_PROMPT, MORPHOLOGY_PART2_USER_PROMPT
from app.services.cut_selector import cut_selector

def normalize_french(text: str) -> str:
    """Corrige quelques coquilles FR courantes sans modifier la casse globale."""
    if not isinstance(text, str) or not text:
        return text

    t = re.sub(r"\s+", " ", text).strip()

    # 1) Corrections d'expressions exactes (multi-mots)
    phrase_fixes = {
        "detail delicat": "détail délicat",
        "ligne fluid": "ligne fluide",
        "a privilegier": "à privilégier",
        "a eviter": "à éviter",
    }
    for bad, good in phrase_fixes.items():
        t = re.sub(rf"\b{re.escape(bad)}\b", good, t, flags=re.IGNORECASE)

    # 2) Corrections de mots (avec frontières \b)
    word_fixes = {
        "details": "détails",
        "detail": "détail",
        "delicat": "délicat",
        "elegant": "élégant",
        "epuree": "épurée",
        "equilibre": "équilibre",
        "ajoutee": "ajoutée",
        "eviter": "éviter",
        "disproportionnee": "disproportionnée",
    }
    for bad, good in word_fixes.items():
        t = re.sub(rf"\b{re.escape(bad)}\b", good, t, flags=re.IGNORECASE)

    return t


def deep_normalize_strings(obj):
    """Applique normalize_french() à toutes les valeurs string d’un dict/list."""
    if isinstance(obj, dict):
        return {k: deep_normalize_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [deep_normalize_strings(x) for x in obj]
    if isinstance(obj, str):
        return normalize_french(obj)
    return obj


class MorphologyService:
    def __init__(self):
        self.openai = openai_client
        print(f"✅ MorphologyService loaded. Has _generate_default_recommendations: {hasattr(self, '_generate_default_recommendations')}")

    
    @staticmethod
    def safe_format(template: str, **kwargs) -> str:
        """Format un template en ignorant les clés manquantes - ULTRA ROBUSTE"""
        # Utiliser une classe defaultdict pour retourner vide string pour ANY missing key
        class SafeDict(dict):
            def __missing__(self, key):
                return ""  # Retourner "" pour toute clé manquante au lieu de lever KeyError
        
        safe_dict = SafeDict(kwargs)
        try:
            return template.format_map(safe_dict)
        except Exception as e:
            print(f"⚠️ Erreur format_map: {str(e)}")
            return template
    
    @staticmethod
    def clean_json_string(content: str) -> str:
        """Nettoie une réponse JSON pour éviter les erreurs de parsing"""
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        content = content.replace('\x00', '')
        content = re.sub(r'\\([éèêëàâäùûüôöîïœæ])', r'\1', content)
        return content
    @staticmethod
    def sanitize_json_multiline_strings(raw: str) -> str:
        """
        Rend un JSON beaucoup plus parseable en supprimant les retours à la ligne
        ET tabulations à l'intérieur des strings JSON (entre guillemets).
        Objectif: éviter les JSON invalides quand OpenAI casse une string sur 2 lignes.
        """
        if not raw:
            return raw

        out = []
        in_string = False
        escape = False

        for ch in raw:
            if in_string:
                if escape:
                    escape = False
                    out.append(ch)
                    continue

                if ch == "\\":
                    escape = True
                    out.append(ch)
                    continue

                # Interdire retours ligne / tabs DANS une string JSON
                if ch in ("\n", "\r", "\t"):
                    out.append(" ")
                    continue

                if ch == '"':
                    in_string = False

                out.append(ch)
            else:
                if ch == '"':
                    in_string = True
                out.append(ch)

        return "".join(out)
 
    @staticmethod
    def merge_body_parts(onboarding_parts: list, openai_parts: list) -> list:
        """Fusionne les parties du corps en déduplicant"""
        if not openai_parts:
            openai_parts = []
        if not onboarding_parts:
            onboarding_parts = []
        
        onboarding_normalized = {part.lower().strip(): part for part in onboarding_parts}
        openai_normalized = {part.lower().strip(): part for part in openai_parts}
        
        merged = {}
        for norm, orig in onboarding_normalized.items():
            merged[norm] = orig
        for norm, orig in openai_normalized.items():
            if norm not in merged:
                merged[norm] = orig
        
        return list(merged.values())
    
    async def analyze(self, user_data: dict) -> dict:
        """Analyse morphologie MVP EN 2 APPELS SÉQUENTIELS"""
        print("\n" + "=" * 80)
        print("💪 PHASE MORPHOLOGIE MVP (2 appels)")
        print("=" * 80)

        body_photo_url = user_data.get("body_photo_url")
        has_photo = bool(body_photo_url)
        if not has_photo:
            print("ℹ️ Pas de photo de corps — mode mensurations")

        print("\n📋 RÉCUPÉRATION MORPHOLOGY GOALS DU ONBOARDING")
        profile = user_data.get("profile", {})
        onboarding_data = profile.get("onboarding_data", {})
        morphology_goals = onboarding_data.get("morphology_goals", {})

        onboarding_highlight_parts = morphology_goals.get("body_parts_to_highlight", [])
        onboarding_minimize_parts = morphology_goals.get("body_parts_to_minimize", [])

        print(f"   • À valoriser (onboarding): {onboarding_highlight_parts}")
        print(f"   • À minimiser (onboarding): {onboarding_minimize_parts}")

        part1_result = {}
        part2_result = {}
        silhouette = None  # ✅ FIX: garantit que la variable existe même si analyze_image échoue
        computed_silhouette = None

        silhouette_declaree = (user_data.get("silhouette_declaree") or "").strip().upper()[:1]
        if silhouette_declaree not in ("A", "V", "X", "H", "O"):
            silhouette_declaree = ""
        used_declared = False

        try:
            # ====================================================================
            # APPEL 1/2: MORPHOLOGY PART 1 - SILHOUETTE (VISION)
            # ====================================================================
            print("\n" + "█" * 80)
            print("█ APPEL 1/2: MORPHOLOGY PART 1 - SILHOUETTE + BODY ANALYSIS (VISION)")
            print("█" * 80)

            self.openai.set_system_prompt(MORPHOLOGY_PART1_SYSTEM_PROMPT)

            if has_photo:
                self.openai.set_context("Morphology Part 1", "PART 1: Silhouette (vision)")

                user_prompt_part1 = self.safe_format(
                    MORPHOLOGY_PART1_USER_PROMPT,
                    body_photo_url=body_photo_url,
                    shoulder_circumference=user_data.get("shoulder_circumference", 0),
                    waist_circumference=user_data.get("waist_circumference", 0),
                    hip_circumference=user_data.get("hip_circumference", 0),
                    bust_circumference=user_data.get("bust_circumference", 0)
                )

                response_part1 = await self.openai.analyze_image(
                    image_urls=[body_photo_url],
                    prompt=user_prompt_part1,
                    max_tokens=800
                )
            else:
                self.openai.set_context("Morphology Part 1", "PART 1: Silhouette (mensurations)")

                computed_silhouette = self._compute_silhouette_from_measurements(
                    shoulder=user_data.get("shoulder_circumference", 0),
                    bust=user_data.get("bust_circumference", 0),
                    waist=user_data.get("waist_circumference", 0),
                    hip=user_data.get("hip_circumference", 0),
                )

                print(f"   • Silhouette calculée: {computed_silhouette or 'indéterminée'}")

                if not computed_silhouette and silhouette_declaree:
                    computed_silhouette = silhouette_declaree
                    used_declared = True
                    print(f"   • Silhouette déclarée par la cliente : {silhouette_declaree}")
                elif not computed_silhouette:
                    print("   ⚠️ Ni mensurations ni silhouette déclarée — repli 'H' dans le prompt")

                user_prompt_part1 = self.safe_format(
                    MORPHOLOGY_PART1_NOPHOTO_USER_PROMPT,
                    silhouette_computed=computed_silhouette or "H",
                    shoulder_circumference=user_data.get("shoulder_circumference", 0),
                    waist_circumference=user_data.get("waist_circumference", 0),
                    hip_circumference=user_data.get("hip_circumference", 0),
                    bust_circumference=user_data.get("bust_circumference", 0)
                )

                response_part1 = await self.openai.call_chat(
                    prompt=user_prompt_part1,
                    model="gpt-4-turbo",
                    max_tokens=800
                )

            content_part1 = response_part1.get("content", "")
            content_part1_clean = self.clean_json_string(content_part1)

            try:
                part1_result = json.loads(content_part1_clean)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', content_part1_clean, re.DOTALL)
                if json_match:
                    try:
                        part1_result = json.loads(json_match.group())
                    except Exception:
                        part1_result = {}
                else:
                    part1_result = {}

            silhouette = part1_result.get("silhouette_type")

            if not silhouette:
                silhouette = self._compute_silhouette_from_measurements(
                    shoulder=user_data.get("shoulder_circumference", 0),
                    bust=user_data.get("bust_circumference", 0),
                    waist=user_data.get("waist_circumference", 0),
                    hip=user_data.get("hip_circumference", 0),
                )
                if silhouette:
                    print(f"   ⚠️ Silhouette calculée depuis mensurations (fallback photo): {silhouette}")
                else:
                    print("   ⚠️ Mensurations insuffisantes — silhouette non déterminée")

            if not has_photo and computed_silhouette:
                if silhouette != computed_silhouette:
                    print(f"   ⚠️ GPT a renvoyé '{silhouette}' — forçage sur '{computed_silhouette}'")
                silhouette = computed_silhouette
                part1_result["silhouette_type"] = computed_silhouette

            styling_objectives = part1_result.get("styling_objectives", []) or ["Harmoniser la silhouette"]
            body_parts_highlight = part1_result.get("body_parts_to_highlight", []) or []
            body_parts_minimize = part1_result.get("body_parts_to_minimize", []) or []

            # ====================================================================
            # APPEL 2/2: MORPHOLOGY PART 2 - MVP ACTIONNABLE
            # ====================================================================
            print("\n" + "█" * 80)
            print("█ APPEL 2/2: MORPHOLOGY PART 2 - RECOMMANDATIONS MVP")
            print("█" * 80)

            self.openai.set_context("Morphology Part 2", "PART 2: Morphology MVP")
            self.openai.set_system_prompt(MORPHOLOGY_PART2_SYSTEM_PROMPT)

            # ── SELECTION DETERMINISTE DES COUPES ─────────────────────────
            # Les souhaits de la cliente priment sur ceux devines par GPT.
            selection_highlight = self.merge_body_parts(
                onboarding_highlight_parts, body_parts_highlight
            )
            selection_minimize = self.merge_body_parts(
                onboarding_minimize_parts, body_parts_minimize
            )

            try:
                taille_cm = int(user_data.get("height") or 0) or None
            except (TypeError, ValueError):
                taille_cm = None

            coupes_selectionnees = cut_selector.selectionner_rapport(
                silhouette=silhouette,
                a_minimiser=selection_minimize,
                a_valoriser=selection_highlight,
                taille_cm=taille_cm,
            )
            print("\n🎯 COUPES SELECTIONNEES PAR LE CODE (zero GPT)")
            for cat, items in coupes_selectionnees.items():
                noms = ", ".join(i["name"] for i in items) or "aucune"
                print(f"   • {cat}: {noms}")

            coupes_imposees = self._formater_coupes_pour_prompt(coupes_selectionnees)

            user_prompt_part2 = self.safe_format(
                MORPHOLOGY_PART2_USER_PROMPT,
                silhouette_type=silhouette,
                styling_objectives=", ".join(styling_objectives),
                body_parts_to_highlight=", ".join(selection_highlight),
                body_parts_to_minimize=", ".join(selection_minimize),
                coupes_imposees=coupes_imposees,
            )

            response_part2 = await self.openai.call_chat(
                prompt=user_prompt_part2,
                model="gpt-4-turbo",
                max_tokens=1800
            )

            content_part2 = response_part2.get("content", "")
            content_part2_clean = self.clean_json_string(content_part2)
            content_part2_clean = self.sanitize_json_multiline_strings(content_part2_clean)

            s = content_part2_clean.find("{")
            e = content_part2_clean.rfind("}") + 1
            if s != -1 and e > s:
                content_part2_clean = content_part2_clean[s:e]

            content_part2_clean = self._repair_broken_json(content_part2_clean)

            try:
                part2_result = json.loads(content_part2_clean)
                print("   ✅ Parsing Part 2 réussi")
            except json.JSONDecodeError as e:
                print(f"   ⚠️ JSON Part 2 invalide: {e}")
                try:
                    part2_result = await self.force_valid_json(
                        content_part2_clean,
                        context="Morphology Part 2 MVP"
                    )
                    print("   ✅ JSON Part 2 corrigé par OpenAI")
                except Exception as fix_err:
                    print(f"   ❌ Correction Part 2 échouée: {fix_err}")
                    part2_result = self._generate_default_morphology_mvp(silhouette)

            # Les noms et visuels viennent du code, pas de GPT.
            # Seul le texte "why" rédigé par GPT est conservé.
            part2_result = self._imposer_coupes(part2_result, coupes_selectionnees)

            # ====================================================================
            # FUSION ONBOARDING + OPENAI POUR PAGE 8
            # ====================================================================
            print("\n" + "=" * 80)
            print("🔗 FUSION ONBOARDING + OPENAI")
            print("=" * 80)

            openai_highlight_parts = part1_result.get("body_parts_to_highlight", [])
            openai_minimize_parts = part1_result.get("body_parts_to_minimize", [])

            merged_highlight_parts = self.merge_body_parts(
                onboarding_highlight_parts,
                openai_highlight_parts
            )
            merged_minimize_parts = self.merge_body_parts(
                onboarding_minimize_parts,
                openai_minimize_parts
            )

            silhouette_explanation = part1_result.get("silhouette_explanation", "")

            openai_highlights = part1_result.get("highlights", {})
            openai_minimizes = part1_result.get("minimizes", {})

            has_openai_highlights = bool(openai_highlights and openai_highlights.get("announcement"))
            has_openai_minimizes = bool(openai_minimizes and openai_minimizes.get("announcement"))

            if has_openai_highlights:
                highlights_data = {
                    "announcement": openai_highlights.get("announcement", ""),
                    "explanation": openai_highlights.get("explanation", ""),
                    "tips": openai_highlights.get("tips", []),
                    "full_text": ""
                }
            else:
                highlights_data = self._format_highlights_for_page8(
                    parties=merged_highlight_parts,
                    silhouette_explanation=silhouette_explanation,
                    onboarding_parties=onboarding_highlight_parts,
                    openai_parties=openai_highlight_parts
                )
                highlights_data.setdefault("tips", [])

            if has_openai_minimizes:
                minimizes_data = {
                    "announcement": openai_minimizes.get("announcement", ""),
                    "explanation": openai_minimizes.get("explanation", ""),
                    "tips": openai_minimizes.get("tips", []),
                    "full_text": ""
                }
            else:
                minimizes_data = self._format_minimizes_for_page8(
                    parties=merged_minimize_parts,
                    silhouette_explanation=silhouette_explanation,
                    onboarding_parties=onboarding_minimize_parts,
                    openai_parties=openai_minimize_parts
                )
                minimizes_data.setdefault("tips", [])

            final_result = {
                "silhouette_type": silhouette,
                "bodyType": silhouette,
                "morphology_source": "photo" if has_photo else ("declaree" if used_declared else "measurements"),
                "silhouette_explanation": part1_result.get("silhouette_explanation"),
                "body_parts_to_highlight": part1_result.get("body_parts_to_highlight", []),
                "body_parts_to_minimize": part1_result.get("body_parts_to_minimize", []),
                "body_analysis": part1_result.get("body_analysis"),
                "styling_objectives": part1_result.get("styling_objectives", []),
                "highlights": highlights_data,
                "minimizes": minimizes_data,
                "morphology_mvp": deep_normalize_strings(part2_result),
            }

            print("✅ Morphologie MVP générée avec succès")
            print("\n" + "=" * 80 + "\n")
            return final_result

        except Exception as e:
            print(f"\n❌ EXCEPTION: {str(e)}")
            call_tracker.log_error("Morphology", str(e))

            import traceback
            traceback.print_exc()

            return {
                "silhouette_type": part1_result.get("silhouette_type") or silhouette,
                "morphology_source": "photo" if has_photo else ("declaree" if used_declared else "measurements"),
                "silhouette_explanation": part1_result.get("silhouette_explanation"),
                "body_parts_to_highlight": part1_result.get("body_parts_to_highlight", []),
                "body_parts_to_minimize": part1_result.get("body_parts_to_minimize", []),
                "body_analysis": part1_result.get("body_analysis"),
                "styling_objectives": part1_result.get("styling_objectives", []),
                "bodyType": part1_result.get("silhouette_type") or silhouette,
                "highlights": part1_result.get("highlights", {}),
                "minimizes": part1_result.get("minimizes", {}),
                "morphology_mvp": self._generate_default_morphology_mvp(
                    part1_result.get("silhouette_type", "O")
                ),
            }

    @staticmethod
    def _formater_coupes_pour_prompt(selection: dict) -> str:
        """Texte lisible des coupes imposees, insere dans le prompt Part 2."""
        libelles = {"haut": "HAUTS", "bas": "BAS", "robe": "ROBES ET COMBINAISONS",
                    "veste": "VESTES", "manteau": "MANTEAUX"}
        lignes = []
        for cat, titre in libelles.items():
            items = selection.get(cat) or []
            if not items:
                continue
            lignes.append(f"{titre} :")
            for it in items:
                effets = []
                if it.get("flatte"):
                    effets.append("met en valeur : " + ", ".join(it["flatte"]))
                if it.get("attenue"):
                    effets.append("attenue : " + ", ".join(it["attenue"]))
                suffixe = f"  ({' | '.join(effets)})" if effets else ""
                lignes.append(f"  - {it['name']}{suffixe}")
        return "\n".join(lignes)

    @staticmethod
    def _why_de_secours(coupe: dict) -> str:
        """Texte deterministe si GPT n'a rien redige pour cette coupe."""
        articles = {"taille": "votre taille", "ventre": "votre ventre",
                    "poitrine": "votre poitrine", "decollete": "votre décolleté",
                    "hanches": "vos hanches", "jambes": "vos jambes",
                    "epaules": "vos épaules", "bras": "vos bras"}
        fl = [articles.get(z, z) for z in coupe.get("flatte") or []]
        at = [articles.get(z, z) for z in coupe.get("attenue") or []]
        if fl and at:
            return f"Cette coupe met en valeur {' et '.join(fl)} tout en atténuant {' et '.join(at)}."
        if fl:
            return f"Cette coupe met en valeur {' et '.join(fl)}."
        if at:
            return f"Cette coupe atténue {' et '.join(at)}."
        return "Une coupe adaptée à votre silhouette."
    
    @staticmethod
    def _imposer_coupes(part2: dict, selection: dict) -> dict:
        """Remplace les noms choisis par GPT par ceux selectionnes par le code,
        en conservant le texte 'why' redige par GPT."""
        if not isinstance(part2, dict):
            return part2
        essentials = part2.get("essentials")
        if not isinstance(essentials, dict):
            return part2

        # jackets du rapport = vestes + manteaux du catalogue
        par_categorie = {
            "tops": list(selection.get("haut") or []),
            "bottoms": list(selection.get("bas") or []),
            "dresses": list(selection.get("robe") or []),
            "jackets": list(selection.get("veste") or []) + list(selection.get("manteau") or []),
        }

        for cle_mvp, coupes in par_categorie.items():
            if not coupes:
                continue
            anciens = essentials.get(cle_mvp)
            anciens = anciens if isinstance(anciens, list) else []
            # GPT recopie les noms a l'identique : on retrouve son texte par
            # le nom, et seulement a defaut par la position.
            par_nom = {}
            for a in anciens:
                if isinstance(a, dict) and a.get("name"):
                    par_nom[a["name"].strip().lower()] = a.get("why") or ""

            nouveaux = []
            for i, c in enumerate(coupes):
                why = par_nom.get(c["name"].strip().lower(), "")
                if not why and i < len(anciens) and isinstance(anciens[i], dict):
                    why = anciens[i].get("why") or ""
                if not why:
                    why = MorphologyService._why_de_secours(c)
                nouveaux.append({
                    "name": c["name"],
                    "why": why,
                    "visual_key": c["visual_key"],
                    "visual_url": c["visual_url"],
                })
            essentials[cle_mvp] = nouveaux

        part2["essentials"] = essentials
        return part2
    
    def _format_highlights_for_page8(self, parties: list, silhouette_explanation: str,
                                     onboarding_parties: list, openai_parties: list) -> dict:
        """
        Génère les highlights pour Page 8
        Utilise silhouette_explanation comme base pour l'explanation
        """
        announcement = ", ".join(parties) if parties else "Votre silhouette"
        
        # L'explanation de base vient de silhouette_explanation
        explanation = silhouette_explanation
        
        # Enrichir avec les sources
        if onboarding_parties and openai_parties:
            explanation += f"\n\nCette analyse combine vos préférences (vous aviez sélectionné: {', '.join(onboarding_parties)}) avec nos recommandations morphologiques (nous suggérons: {', '.join(openai_parties)})."
        elif onboarding_parties:
            explanation += f"\n\nVous aviez sélectionné ces parties à valoriser: {', '.join(onboarding_parties)}."
        elif openai_parties:
            explanation += f"\n\nNous recommandons de valoriser: {', '.join(openai_parties)}."
        
        full_text = f"""ANNONCE: {announcement}

EXPLICATION: {explanation}"""
        
        return {
            "announcement": announcement,
            "explanation": explanation,
            "full_text": full_text
        }

    def _format_minimizes_for_page8(self, parties: list, silhouette_explanation: str,
                                    onboarding_parties: list, openai_parties: list) -> dict:
        """
        Génère les minimizes pour Page 8
        Utilise silhouette_explanation comme base pour l'explanation
        """
        announcement = ", ".join(parties) if parties else "Votre silhouette"

        # Base explanation
        explanation = silhouette_explanation or "Certaines zones peuvent être visuellement atténuées par des coupes et volumes mieux placés."

        # Enrichir avec les sources
        if onboarding_parties and openai_parties:
            explanation += (
                f"\n\nCette analyse combine vos préférences (vous aviez sélectionné: {', '.join(onboarding_parties)}) "
                f"avec nos recommandations morphologiques (nous suggérons: {', '.join(openai_parties)})."
            )
        elif onboarding_parties:
            explanation += f"\n\nVous aviez sélectionné ces zones à minimiser: {', '.join(onboarding_parties)}."
        elif openai_parties:
            explanation += f"\n\nNous recommandons de minimiser visuellement: {', '.join(openai_parties)}."

        full_text = f"""ANNONCE: {announcement}

EXPLICATION: {explanation}"""

        return {
            "announcement": announcement,
            "explanation": explanation,
            "full_text": full_text
        }

    @staticmethod
    def _repair_broken_json(json_str: str) -> str:
        """Répare les JSON partiellement cassés (best-effort)."""
        if not isinstance(json_str, str):
            return ""

        # Enlever guillemets typographiques
        json_str = json_str.replace("“", '"').replace("”", '"').replace("’", "'")

        # Supprimer virgules finales avant } ou ]
        json_str = re.sub(r",\s*([}\]])", r"\1", json_str)

        # Fermer accolades manquantes
        open_count = json_str.count("{")
        close_count = json_str.count("}")
        if open_count > close_count:
            json_str += "}" * (open_count - close_count)

        open_count = json_str.count("[")
        close_count = json_str.count("]")
        if open_count > close_count:
            json_str += "]" * (open_count - close_count)

        return json_str

    async def force_valid_json(self, raw_content: str, context: str) -> dict:
        """
        Redemande à OpenAI de corriger STRICTEMENT un JSON invalide.
        Version durcie: nettoyage + extraction + réparation légère + sanitize multiline + parsing robuste.
        """
        # 0) Sécurité
        raw_content = raw_content or ""

        # 1) Pré-nettoyage local (enlever fences, NUL, accents échappés, etc.)
        cleaned = self.clean_json_string(raw_content)

        # 2) Extraire le plus gros bloc JSON (évite le texte parasite)
        s = cleaned.find("{")
        e = cleaned.rfind("}") + 1
        if s != -1 and e > s:
            cleaned = cleaned[s:e]

        # 3) Réparation locale minimale (virgules finales, guillemets typographiques, crochets/accolades manquants)
        cleaned = self._repair_broken_json(cleaned)

        # 4) Patch anti-retours-ligne dans strings JSON
        cleaned = self.sanitize_json_multiline_strings(cleaned)

        repair_prompt = f"""
        Tu vas recevoir un JSON invalide. Tu dois renvoyer UNIQUEMENT un JSON strict valide.

        Règles:
        - Réponds uniquement par un objet JSON qui commence par {{ et se termine par }}.
        - Aucun texte avant ou après. Aucun Markdown. Aucun ```json.
        - Guillemets doubles uniquement.
        - Aucune virgule finale.
        - Si une valeur contient des retours à la ligne, remplace-les par un espace.
        - Conserve exactement la structure et les clés, ne supprime pas de sections.

        JSON À CORRIGER:
        {cleaned}
        """.strip()

        self.openai.set_context(f"{context} - JSON FIX", "")
        self.openai.set_system_prompt(
            "Tu es un validateur JSON strict. Tu renvoies uniquement un JSON strict valide, sans Markdown, sans commentaire."
        )

        response = await self.openai.call_chat(
            prompt=repair_prompt,
            model="gpt-4-turbo",
            max_tokens=3500
        )

        content = (response.get("content", "") or "").strip()

        # 5) Re-nettoyage + re-extraction + re-sanitize avant parsing final
        content = self.clean_json_string(content)
        s = content.find("{")
        e = content.rfind("}") + 1
        if s != -1 and e > s:
            content = content[s:e]
        content = self._repair_broken_json(content)
        content = self.sanitize_json_multiline_strings(content)

        return json.loads(content)

    def _generate_default_morphology_mvp(self, silhouette: str) -> dict:
        """Fallback MVP compact si Part 2 échoue."""
        return {
            "essentials": {
                "tops": [
                    {"name": "Top col V fluide", "why": "allonge le haut du corps"},
                    {"name": "Blouse légèrement structurée", "why": "apporte de la tenue sans durcir"},
                    {"name": "Haut cache coeur", "why": "dessine une taille visuelle"},
                ],
                "bottoms": [
                    {"name": "Pantalon taille haute droit", "why": "allonge la jambe"},
                    {"name": "Jean brut coupe droite", "why": "équilibre les volumes"},
                    {"name": "Jupe midi fluide", "why": "adoucit la silhouette"},
                ],
                "dresses_jackets": [
                    {"name": "Robe portefeuille", "why": "structure la silhouette"},
                    {"name": "Robe empire sobre", "why": "allège la zone centrale"},
                    {"name": "Veste cintrée ouverte", "why": "crée une ligne verticale"},
                ],
                "shoes_accessories": [
                    {"name": "Escarpins ou bottines à talon moyen", "why": "élancent la silhouette"},
                    {"name": "Collier long discret", "why": "renforce la verticalité"},
                    {"name": "Ceinture fine", "why": "marque la taille sans couper"},
                ],
            },
            "avoid": [
                {"name": "Hauts trop boxy", "why": "effacent la structure du buste"},
                {"name": "Volumes concentrés au milieu du corps", "why": "alourdissent visuellement"},
                {"name": "Pièces trop raides ou trop larges", "why": "cassent l harmonie générale"},
            ],
            "outfit_formulas": [
                {
                    "occasion": "Quotidien",
                    "pieces": ["Top fluide", "Jean droit taille haute", "Veste ouverte", "Bottines"],
                    "why_it_works": "silhouette lisible, confortable et équilibrée",
                },
                {
                    "occasion": "Travail",
                    "pieces": ["Blouse structurée", "Pantalon droit", "Blazer cintré", "Escarpins"],
                    "why_it_works": "tenue élégante qui affine et structure",
                },
                {
                    "occasion": "Sortie",
                    "pieces": ["Robe portefeuille", "Talons moyens", "Boucles discrètes", "Mini sac structuré"],
                    "why_it_works": "met en valeur sans surcharger la silhouette",
                },
            ],
            "shopping_priorities": [
                "Un haut col V ou cache coeur",
                "Un pantalon droit taille haute",
                "Une robe portefeuille unie",
                "Une veste cintrée facile à superposer",
                "Une paire de chaussures qui allonge la jambe",
            ],
        }
    @staticmethod
    def _compute_silhouette_from_measurements(
        shoulder: float,
        bust: float,
        waist: float,
        hip: float,
    ) -> str:
        """
        Calcule la silhouette morphologique à partir des mensurations seules.
        Utilisé comme fallback si l'analyse vision OpenAI échoue.
        Retourne: "A" | "V" | "X" | "H" | "O"
        """
        if not all([shoulder, hip, waist]):
            return None  # Mensurations insuffisantes → on ne peut pas décider

        ref = bust if bust else shoulder

        # O : taille peu différente des hanches (corps arrondi, peu de définition)
        if waist >= hip * 0.88:
            return "O"

        # A : hanches significativement plus larges que les épaules
        if hip > shoulder * 1.05:
            return "A"

        # V : épaules significativement plus larges que les hanches
        if shoulder > hip * 1.05:
            return "V"

        # X : épaules ≈ hanches ET taille bien marquée
        if waist <= hip * 0.75:
            return "X"

        # H : épaules ≈ hanches, taille peu marquée
        return "H"
 
    def _generate_default_recommendations(self, silhouette: str) -> dict:
        """Génère des recommandations par défaut si OpenAI échoue (structure SAFE complète)"""
        print("   ✅ Génération recommandations par défaut")

        base_category = lambda label: {
            "introduction": f"Recommandations générales pour les {label}.",
            "recommandes": [
                {
                    "cut_display": "Coupe adaptée à votre silhouette",
                    "why": "Cette coupe aide à équilibrer les volumes et à structurer la silhouette."
                }
            ],
            "a_eviter": [
                {
                    "cut_display": "Coupe non structurée",
                    "why": "Elle peut déséquilibrer visuellement la silhouette et alourdir la ligne."
                }
            ]
        }

        defaults = {
            "A": {
                "hauts": {
                    "introduction": "Pour une silhouette A, l’objectif est de valoriser le haut du corps et d’apporter de la structure aux épaules.",
                    "recommandes": [
                        {"cut_display": "Haut structuré", "why": "Crée du volume au haut"},
                        {"cut_display": "Encolure V", "why": "Allonge le buste"},
                        {"cut_display": "Col rond ajusté", "why": "Met en avant les épaules"},
                        {"cut_display": "Haut échancré", "why": "Crée de la profondeur"},
                        {"cut_display": "Manches montantes", "why": "Définit les épaules"},
                        {"cut_display": "Peplum placé haut", "why": "Donne du relief au haut du corps"},
                    ],
                    "a_eviter": [
                        {"cut_display": "Haut moulant long", "why": "Accentue le contraste haut/bas"},
                        {"cut_display": "Tunique informe", "why": "Retire la structure du buste"},
                        {"cut_display": "Col bateau très large", "why": "Élargit artificiellement"},
                        {"cut_display": "Haut oversize sans taille", "why": "Perd les proportions"},
                        {"cut_display": "Manches très bouffantes", "why": "Peut surcharger le haut"},
                    ]
                },
                "bas": {
                    "introduction": "Pour une silhouette A, l’objectif est d’allonger la jambe et d’équilibrer la zone des hanches.",
                    "recommandes": [
                        {"cut_display": "Jean taille haute droit", "why": "Allonge les jambes"},
                        {"cut_display": "Pantalon droit", "why": "Équilibre les hanches"},
                        {"cut_display": "Jupe évasée", "why": "Harmonise la ligne des hanches"},
                        {"cut_display": "Pantalon flare léger", "why": "Crée une verticalité"},
                        {"cut_display": "Jupe plissée fine", "why": "Structure sans épaissir"},
                        {"cut_display": "Couleurs plus sombres en bas", "why": "Affinent visuellement"},
                    ],
                    "a_eviter": [
                        {"cut_display": "Pantalon moulant clair", "why": "Met l’accent sur les hanches"},
                        {"cut_display": "Short très court", "why": "Raccourcit la jambe"},
                        {"cut_display": "Pantalon très large", "why": "Élargit la silhouette"},
                        {"cut_display": "Jupe portefeuille épaisse", "why": "Ajoute du volume latéral"},
                        {"cut_display": "Motifs larges sur les hanches", "why": "Grossissent visuellement"},
                    ]
                },
                "robes": base_category("robes"),
                "vestes": base_category("vestes"),
                "maillot_lingerie": base_category("maillots / lingerie"),
                "chaussures": base_category("chaussures"),
                "accessoires": base_category("accessoires"),
            }
        }

        result = defaults.get(silhouette, defaults["A"])

        for category in ["hauts", "bas", "robes", "vestes", "maillot_lingerie", "chaussures", "accessoires"]:
            if category not in result:
                result[category] = base_category(category)
            result[category].setdefault("introduction", "")
            result[category].setdefault("recommandes", [])
            result[category].setdefault("a_eviter", [])

        return {"recommendations": result}

morphology_service = MorphologyService()