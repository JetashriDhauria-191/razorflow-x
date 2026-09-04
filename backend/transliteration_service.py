import re
from typing import Dict, Any, Optional, Tuple

class TransliterationService:
    """
    Romanized Transliteration and Typo Understanding Service.
    Maps Hinglish, Tanglish, Telugish, Manglish phrases to standardized English meaning.
    """
    TRANSLITERATION_GLOSSARY = {
        "joota": ("shoes", "footwear"),
        "jootay": ("shoes", "footwear"),
        "juta": ("shoes", "footwear"),
        "joote": ("shoes", "footwear"),
        "seruppu": ("shoes", "footwear"),
        "seppu": ("shoes", "footwear"),
        "cheppulu": ("shoes", "footwear"),
        "chappal": ("shoes", "footwear"),
        "chappals": ("shoes", "footwear"),
        
        "hedfone": ("headphones", "audio"),
        "headfon": ("headphones", "audio"),
        "headphne": ("headphones", "audio"),
        "earphone": ("headphones", "audio"),
        
        "laptp": ("laptop", "computers"),
        "lappi": ("laptop", "computers"),
        
        "iphne": ("phone", "smartphones"),
        "iphon": ("phone", "smartphones"),
        "mobail": ("phone", "smartphones"),
        
        "ghadi": ("smartwatch", "wearables"),
        "ghari": ("smartwatch", "wearables"),
        "kadigaram": ("smartwatch", "wearables"),
        
        "kapda": ("clothing", "fashion"),
        "kapde": ("clothing", "fashion"),
        "thuni": ("clothing", "fashion"),
        "satttai": ("clothing", "fashion"),
        "kamij": ("clothing", "fashion"),
        "chokka": ("clothing", "fashion"),
        
        "pankha": ("appliances", "appliances"),
        "kursi": ("furniture", "furniture"),
        "sabun": ("beauty", "personal_care"),
        "chashma": ("accessories", "accessories"),
        "kalam": ("stationery", "stationery"),
        "kitab": ("stationery", "stationery"),
        "khilona": ("toys", "toys"),
        "khilone": ("toys", "toys")
    }

    INTENT_MODIFIERS = {
        "nalla": "best", "accha": "best", "achha": "best", "sasta": "cheapest", "mehnga": "premium",
        "chahiye": "intent_buy", "venum": "intent_buy", "kavale": "intent_buy", "venam": "intent_buy",
        "dikhao": "intent_show", "kaatu": "intent_show", "chupinchu": "intent_show", "kaanikoo": "intent_show",
        "under": "budget_max", "below": "budget_max", "andar": "budget_max", "kulla": "budget_max", "lopala": "budget_max"
    }

    def normalize_transliteration(self, query: str) -> Dict[str, Any]:
        q_lower = query.lower().strip()
        tokens = re.split(r'\s+', q_lower)
        
        detected_category = None
        category_intent = None
        suggested_typo = None
        
        for t in tokens:
            if t in self.TRANSLITERATION_GLOSSARY:
                target_word, cat = self.TRANSLITERATION_GLOSSARY[t]
                detected_category = cat
                category_intent = target_word
                if t in ["hedfone", "headfon", "laptp", "iphne", "iphon"]:
                    suggested_typo = target_word
                break

        return {
            "is_transliterated": detected_category is not None,
            "category": detected_category,
            "product_intent": category_intent,
            "suggested_typo": suggested_typo
        }

transliteration_service = TransliterationService()
