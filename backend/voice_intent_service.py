from typing import Dict, Any, Optional
from .language_service import language_service
from .product_alias_service import product_alias_service
from .transliteration_service import transliteration_service

class VoiceIntentService:
    """
    Handles Voice Commerce Intent Processing.
    Produces transparent 'YOU SAID' and 'UNDERSTOOD AS' breakdowns.
    """
    def process_voice_transcript(self, transcript: str, active_language: Optional[str] = None) -> Dict[str, Any]:
        norm = language_service.normalize_multilingual_query(transcript, active_lang=active_language)
        
        lang_code = norm.get("detected_language", "en")
        lang_meta = language_service.SUPPORTED_LANGUAGES.get(lang_code, language_service.SUPPORTED_LANGUAGES["en"])
        
        category = norm.get("category")
        budget = norm.get("budget")
        intent_type = norm.get("intent_type", "DISCOVERY")

        # Build clear human-readable 'UNDERSTOOD AS' string
        understood_parts = []
        if intent_type == "CHEAPEST":
            understood_parts.append("Budget / Affordable")
        elif intent_type == "BEST_RATED":
            understood_parts.append("Top-Rated")
        elif intent_type == "PREMIUM":
            understood_parts.append("Premium")
        else:
            understood_parts.append("Show")

        if category:
            cat_name = product_alias_service.get_canonical_name(category)
            understood_parts.append(cat_name)
        else:
            understood_parts.append("Relevant Products")

        if budget:
            understood_parts.append(f"under ₹{budget:,.0f}")

        understood_as = " ".join(understood_parts)

        return {
            "you_said": transcript,
            "understood_as": understood_as,
            "detected_language_code": lang_code,
            "detected_language_name": lang_meta["name"],
            "category": category,
            "budget": budget,
            "intent_type": intent_type,
            "confidence": norm.get("confidence", 0.9)
        }

voice_intent_service = VoiceIntentService()
