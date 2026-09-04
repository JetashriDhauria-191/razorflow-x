from typing import Dict, Any, List, Optional
from .product_providers.aggregator import provider_aggregator
from .product_providers.base import NormalizedProduct
from .language_service import language_service
from .product_alias_service import product_alias_service
from .transliteration_service import transliteration_service
from .recommendation_engine import recommendation_engine

class SearchService:
    """
    Unified Multilingual Search Pipeline:
    1. Language & Script Detection
    2. Transliteration & Typo Resolution
    3. Category & Budget Normalization
    4. Provider Aggregation (10,000+ items)
    5. Top 4-5 AI Recommendations + Full Results
    """
    def execute_search(
        self,
        query: str,
        active_lang: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        sort_by: str = "relevance",
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        q = (query or "").strip()
        
        # Normalization
        norm = language_service.normalize_multilingual_query(q, active_lang=active_lang)
        lang_code = norm.get("detected_language", "en")
        lang_meta = language_service.SUPPORTED_LANGUAGES.get(lang_code, language_service.SUPPORTED_LANGUAGES["en"])
        
        # Category resolution (Query takes precedence if category is 'all')
        resolved_cat = norm.get("category")
        if category and category != "all":
            resolved_cat = category

        # Budget resolution
        budget = max_price if max_price is not None and max_price > 0 else norm.get("budget")

        intent = {
            "category": resolved_cat,
            "budget": budget,
            "brand": norm.get("brand"),
            "intent_type": norm.get("intent_type", "DISCOVERY"),
            "limit": limit,
            "offset": offset
        }

        # Retrieve aggregated products
        raw_results = provider_aggregator.search_all(q, intent, context={})

        # Apply Sorting
        if sort_by == "price_asc":
            raw_results.sort(key=lambda x: x.price)
        elif sort_by == "price_desc":
            raw_results.sort(key=lambda x: x.price, reverse=True)
        elif sort_by == "rating":
            raw_results.sort(key=lambda x: (x.rating, x.review_count), reverse=True)

        # Generate Top 4-5 Recommendations
        top_recommendations = recommendation_engine.generate_top_recommendations(
            raw_results,
            query=q,
            intent=intent,
            target_count=5
        )

        # Multilingual Insight
        insight_text = language_service.generate_multilingual_insight(
            lang_code=lang_code,
            products=[p.to_dict() for p in raw_results],
            intent=intent
        )

        return {
            "query": q,
            "language_code": lang_code,
            "language_name": lang_meta["name"],
            "confidence": norm.get("confidence", 0.9),
            "category": resolved_cat,
            "budget": budget,
            "total_count": len(raw_results),
            "top_recommendations": top_recommendations,
            "products": [p.to_dict() for p in raw_results],
            "insight": insight_text,
            "data_source": "Storefront Demo Catalogue",
            "is_live_data": False
        }

search_service = SearchService()
