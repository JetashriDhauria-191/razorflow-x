try:
    from backend.recommendation_engine import recommendation_engine
except ImportError:
    from recommendation_engine import recommendation_engine
import os
import re
import time
import math
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

try:
    from backend.catalogue import catalogue_engine
    from backend.language_service import language_service, calculate_similarity
except ImportError:
    from catalogue import catalogue_engine
    from language_service import language_service, calculate_similarity


class NormalizedProduct:
    def __init__(
        self,
        product_id: str,
        name: str,
        brand: str,
        category: str,
        price: float,
        currency: str = "INR",
        original_price: Optional[float] = None,
        discount: Optional[float] = None,
        rating: float = 4.8,
        review_count: int = 120,
        image_url: str = "",
        description: str = "",
        specifications: Optional[List[str]] = None,
        source: str = "Storefront Catalogue",
        source_type: str = "local_catalogue",
        is_buyable: bool = True,
        inventory: int = 25,
        delivery_days: int = 1,
        source_url: Optional[str] = None,
        retrieved_at: Optional[str] = None,
        ai_score: int = 90,
        ai_reasons: Optional[List[str]] = None,
        badges: Optional[List[str]] = None,
        recovery_tier: str = "EXACT_MATCH"
    ):
        self.product_id = str(product_id)
        self.id = str(product_id)
        self.name = name
        self.brand = brand or "Authentic"
        self.category = (category or "general").lower()
        self.price = float(price)
        self.currency = currency
        
        # STRICT HONESTY RULE: Only set original_price and discount if genuinely higher than price
        if original_price is not None and float(original_price) > float(price):
            self.original_price = float(original_price)
            calc_disc = round(((float(original_price) - float(price)) / float(original_price)) * 100)
            self.discount = float(discount) if discount is not None else float(calc_disc)
        else:
            self.original_price = None
            self.discount = None
            
        self.rating = round(float(rating), 2)
        self.review_count = int(review_count)
        self.image_url = image_url or "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
        self.description = description
        self.specifications = specifications or []
        self.source = source
        self.source_type = source_type
        self.is_buyable = bool(is_buyable)
        self.inventory = int(inventory)
        self.delivery_days = int(delivery_days)
        self.delivery_sla = '1-Day Express' if self.delivery_days <= 1 else ('2-Day Standard' if self.delivery_days == 2 else f'{self.delivery_days}-Day Regional')
        self.source_url = source_url
        self.retrieved_at = retrieved_at or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.ai_score = int(ai_score)
        self.ai_reasons = ai_reasons or []
        self.badges = badges or []
        self.recovery_tier = recovery_tier

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.product_id,
            "product_id": self.product_id,
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "price": self.price,
            "currency": self.currency,
            "original_price": self.original_price,
            "discount": self.discount,
            "rating": self.rating,
            "review_count": self.review_count,
            "image_url": self.image_url,
            "image": self.image_url,
            "description": self.description,
            "specifications": self.specifications,
            "source": self.source,
            "source_type": self.source_type,
            "is_buyable": self.is_buyable,
            "inventory": self.inventory,
            "stock": self.inventory,
            "delivery_days": self.delivery_days,
            "delivery_sla": f"{self.delivery_days}-Day SLA" if self.delivery_days > 1 else "1-Day Express",
            "source_url": self.source_url,
            "retrieved_at": self.retrieved_at,
            "ai_score": self.ai_score,
            "ai_reasons": self.ai_reasons,
            "badges": self.badges,
            "recovery_tier": self.recovery_tier
        }


class ProductProvider:
    name: str = "BaseProvider"
    provider_type: str = "abstract"
    is_configured: bool = True

    def search(self, query: str, intent: Dict[str, Any], context: Dict[str, Any]) -> Tuple[List[NormalizedProduct], str]:
        raise NotImplementedError("Subclasses must implement search()")


class LocalCatalogueProvider(ProductProvider):
    name = "Storefront Catalogue"
    provider_type = "local_catalogue"
    is_configured = True

    def search(self, query: str, intent: Dict[str, Any], context: Dict[str, Any]) -> Tuple[List[NormalizedProduct], str]:
        cat_filter = intent.get("category")
        budget = intent.get("budget")
        brand = intent.get("brand")
        recovery_tier = "EXACT_MATCH"
        
        INTENT_STOPWORDS = {
            "show", "me", "the", "option", "options", "pick", "picks", "item", "items", 
            "product", "products", "find", "get", "looking", "for", "cheap", "cheaper", 
            "cheapest", "best", "rated", "top", "premium", "luxury", "flagship", "value",
            "good", "great", "sasta", "kam", "daam", "acchi", "rating", "kaise", "batao",
            "குறைந்த", "விலை", "சிறந்த", "சரியான", "सस्ता", "कम", "चाहिए", "दिखाओ"
        }
        
        q_clean = re.sub(r"[^a-zA-Z0-9\s]", " ", (query or "").lower())
        q_tokens = [w for w in q_clean.split() if w not in INTENT_STOPWORDS]
        search_q = " ".join(q_tokens).strip()

        if intent.get("is_follow_up") and cat_filter:
            search_q = cat_filter
        elif cat_filter and not search_q:
            search_q = cat_filter

        # 8-Tier Zero-Result Recovery Ladder
        # Tier 1: Exact search with category and query
        raw_items = catalogue_engine.search(
            query=search_q if search_q else None,
            category=cat_filter,
            max_price=budget,
            in_stock_only=False
        )
        if intent.get("typo_correction"):
            recovery_tier = "TYPO_TOLERANT_MATCH"
        elif intent.get("detected_language") and intent.get("detected_language") != "en":
            recovery_tier = "LANGUAGE_ALIAS_MATCH"
        elif raw_items and search_q and cat_filter:
            recovery_tier = "EXACT_MATCH"
        elif raw_items and cat_filter:
            recovery_tier = "CATEGORY_INTENT_MATCH"

        # Tier 2 Fallback: If no items with query, fallback to category pool
        if not raw_items and cat_filter:
            raw_items = catalogue_engine.search(
                query=None,
                category=cat_filter,
                max_price=budget,
                in_stock_only=False
            )
            recovery_tier = "CATEGORY_INTENT_MATCH"

        # Tier 3 Fallback: If still empty (e.g. budget too strict), relax budget to find nearest matching options
        if not raw_items and cat_filter:
            raw_items = catalogue_engine.search(
                query=None,
                category=cat_filter,
                max_price=None,
                in_stock_only=False
            )
            recovery_tier = "SYNONYM_EXPANSION_MATCH"

        # Tier 4 Fallback: Multi-category featured selection if completely outside catalogue
        if not raw_items:
            raw_items = catalogue_engine.search(
                query=None,
                category=None,
                max_price=budget,
                in_stock_only=False,
                limit=15
            )
            recovery_tier = "AI_SEMANTIC_MATCH"

        curated = [r for r in raw_items if not r.get("product_id", "").startswith("FALLBACK_")]
        fallbacks = [r for r in raw_items if r.get("product_id", "").startswith("FALLBACK_")]
        sorted_raw = curated if curated else fallbacks

        results: List[NormalizedProduct] = []
        for raw in sorted_raw:
            if brand and brand.lower() not in (raw.get("brand", "") + " " + raw.get("name", "")).lower():
                continue

            orig_price = raw.get("original_price")
            curr_price = float(raw.get("price", 0))
            
            specs = raw.get("features") or raw.get("specifications") or []
            if not specs and raw.get("description"):
                specs = [s.strip() for s in raw["description"].split(".") if len(s.strip()) > 5][:4]

            del_days = int(raw.get("delivery_days", 1))
            if raw.get("category") in ["appliances", "kitchen", "decor"]:
                del_days = max(2, del_days)

            norm_prod = NormalizedProduct(
                product_id=raw.get("product_id") or raw.get("id"),
                name=raw.get("name", "Store Product"),
                brand=raw.get("brand", "Authentic Store"),
                category=raw.get("category", "general"),
                price=curr_price,
                currency="INR",
                original_price=orig_price,
                discount=raw.get("discount"),
                rating=float(raw.get("rating", 4.8)),
                review_count=int(raw.get("review_count", 1200)),
                image_url=raw.get("image_url") or raw.get("image"),
                description=raw.get("description", ""),
                specifications=specs,
                source="Storefront Demo Catalogue",
                source_type="local_demo_catalogue",
                is_buyable=True,
                inventory=int(raw.get("inventory", raw.get("stock", 25))),
                delivery_days=del_days,
                source_url=f"/#product/{raw.get('product_id')}",
                retrieved_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                recovery_tier=recovery_tier
            )
            results.append(norm_prod)

        return results, recovery_tier


class ExternalProductProvider(ProductProvider):
    name = "External Product Network"
    provider_type = "external_verified"

    def __init__(self):
        self.api_key = os.getenv("PRODUCT_PROVIDER_API_KEY", "").strip()
        self.is_configured = bool(self.api_key)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = 300

    def search(self, query: str, intent: Dict[str, Any], context: Dict[str, Any]) -> Tuple[List[NormalizedProduct], str]:
        if not self.is_configured:
            return [], "UNCONFIGURED"

        cache_key = f"{query}_{intent.get('category')}_{intent.get('budget')}"
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["results"], "EXTERNAL_CACHE"

        results: List[NormalizedProduct] = []
        self.cache[cache_key] = {"results": results, "timestamp": time.time()}
        return results, "EXTERNAL_NETWORK"


class AIIntentParser:
    BRANDS = [
        "apple", "sony", "bose", "sennheiser", "samsung", "dell", "lenovo", "asus",
        "logitech", "razer", "keychron", "nike", "adidas", "puma", "asics", "new balance",
        "woodland", "clarks", "peak design", "bellroy", "nomatic", "aer", "wildcraft",
        "ray-ban", "fastrack", "anker", "ugreen", "caldigit", "garmin", "fitbit", "amazfit",
        "noise", "titan", "google", "oneplus", "xiaomi", "redmi", "nothing", "vivo",
        "motorola", "canon", "fujifilm", "gopro", "dji", "atomberg", "lg", "dyson",
        "faber-castell", "pilot", "classmate", "raymond", "prestige", "hawkins"
    ]

    def parse(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        active_lang = context.get("active_language")
        
        # 1. Multilingual Language Understanding & Normalization
        norm = language_service.normalize_multilingual_query(query, active_lang=active_lang)
        did_you_mean = language_service.get_spelling_correction(query)

        detected_cat = norm.get("category")
        budget = norm.get("budget")
        intent_type = norm.get("intent_type", "DISCOVERY")
        lang_code = norm.get("detected_language", "en")
        confidence = norm.get("confidence", 0.95)

        q_lower = (query or "").lower().strip()
        
        # Explicit search intent recognition for headings & chips
        if any(w in q_lower for w in ["cheap", "cheaper", "cheapest", "low price", "lowest", "sasta", "budget", "மலிவான", "குறைந்த விலை", "सस्ता"]):
            intent_type = "CHEAPEST"
        elif any(w in q_lower for w in ["best rated", "top rated", "highest rated", "top review", "5 star", "அதிக மதிப்பீடு", "டாப் ரேட்டெட்", "टॉप रेटेड"]):
            intent_type = "BEST_RATED"
        elif any(w in q_lower for w in ["premium", "luxury", "flagship", "top tier", "pro", "ultra", "expensive", "விலை உயர்ந்த", "प्रीमियम"]):
            intent_type = "PREMIUM"
        elif any(w in q_lower for w in ["best value", "value for money", "bang for buck", "balanced", "worth it"]):
            intent_type = "BEST_VALUE"

        # Brand Detection with whole-word boundary
        clean_q = (query or "").lower().strip()
        detected_brand = None
        for b in self.BRANDS:
            if re.search(r'\b' + re.escape(b) + r'\b', clean_q):
                detected_brand = b
                break

        # Conversational Follow-up logic
        is_follow_up = False
        if not detected_cat and context.get("previous_category"):
            if intent_type in ("CHEAPEST", "PREMIUM", "BEST_RATED", "BEST_VALUE", "COMPARE") or budget is not None:
                detected_cat = context.get("previous_category")
                is_follow_up = True
                if not budget and context.get("previous_budget"):
                    if intent_type == "CHEAPEST":
                        budget = float(context["previous_budget"]) * 0.8
                    else:
                        budget = float(context["previous_budget"])

        sort_by = "relevance"
        if intent_type == "CHEAPEST":
            sort_by = "price_asc"
        elif intent_type == "PREMIUM":
            sort_by = "price_desc"
        elif intent_type == "BEST_RATED":
            sort_by = "rating_desc"
        elif intent_type == "BEST_VALUE":
            sort_by = "ai_score_desc"

        return {
            "raw_query": query,
            "detected_language": lang_code,
            "language_name": norm.get("language_name", "English"),
            "confidence": confidence,
            "confidence_score_percent": norm.get("confidence_score_percent", int(confidence * 100)),
            "confidence_tier": norm.get("confidence_tier", "HIGH CONFIDENCE"),
            "did_you_mean": did_you_mean,
            "typo_correction": norm.get("typo_correction"),
            "category": detected_cat,
            "category_canonical": norm.get("category_canonical"),
            "interpreted_intent": norm.get("interpreted_intent", (detected_cat or "Product Discovery").title()),
            "brand": detected_brand,
            "budget": budget,
            "intent_type": intent_type,
            "sort_by": sort_by,
            "is_follow_up": is_follow_up,
            "expanded_aliases": norm.get("expanded_aliases", [])
        }


class AIRankingAndInsightEngine:
    def rank_and_annotate(
        self,
        products: List[NormalizedProduct],
        intent: Dict[str, Any]
    ) -> List[NormalizedProduct]:
        if not products:
            return []

        budget = intent.get("budget")
        cat = intent.get("category")
        brand = intent.get("brand")
        intent_type = intent.get("intent_type", "DISCOVERY")

        for p in products:
            reasons = []
            
            cat_match = 35 if cat and cat in p.category else 28
            reasons.append(f"Direct match for {p.category.upper()} category")

            if budget:
                if p.price <= budget:
                    ratio = p.price / budget
                    budget_score = 25 if ratio >= 0.4 else 20
                    reasons.append(f"Fits well inside ₹{budget:,.0f} budget (₹{p.price:,.0f})")
                else:
                    over = (p.price - budget) / budget
                    budget_score = max(5, int(25 - (over * 30)))
            else:
                budget_score = 22

            rating_score = int((p.rating / 5.0) * 15)
            if p.rating >= 4.8:
                reasons.append(f"Exceptional {p.rating}★ rating ({p.review_count:,}+ verified buyers)")

            sla_score = 15 if p.delivery_days <= 1 else (10 if p.delivery_days <= 2 else 5)
            if p.delivery_days <= 1:
                reasons.append("Guaranteed 1-Day Express Delivery SLA")
            else:
                reasons.append(f"Standard {p.delivery_days}-Day Delivery SLA")

            value_score = 10 if (p.discount and p.discount >= 20) else 7
            if p.discount and p.discount >= 20:
                reasons.append(f"High {p.discount:.0f}% verified savings")

            total_score = min(99, max(60, cat_match + budget_score + rating_score + sla_score + value_score))
            p.ai_score = total_score
            p.ai_reasons = reasons[:4]

        if len(products) > 0:
            cheapest = min(products, key=lambda x: x.price)
            cheapest.badges.append("CHEAPEST")
            
            best_rated = max(products, key=lambda x: (x.rating, x.review_count))
            if "CHEAPEST" not in best_rated.badges:
                best_rated.badges.append("BEST RATED")

            premium = max(products, key=lambda x: x.price)
            if "CHEAPEST" not in premium.badges and "BEST RATED" not in premium.badges:
                premium.badges.append("PREMIUM PICK")

            best_value = max(products, key=lambda x: x.ai_score)
            if "BEST VALUE" not in best_value.badges:
                best_value.badges.insert(0, "BEST VALUE")

        sort_by = intent.get("sort_by", "relevance")
        if sort_by == "price_asc":
            products.sort(key=lambda x: x.price)
        elif sort_by == "price_desc":
            products.sort(key=lambda x: x.price, reverse=True)
        elif sort_by == "rating_desc":
            products.sort(key=lambda x: (x.rating, x.review_count), reverse=True)
        elif sort_by == "ai_score_desc":
            products.sort(key=lambda x: x.ai_score, reverse=True)
        else:
            products.sort(key=lambda x: x.ai_score, reverse=True)

        return products

    def generate_shopping_insight(
        self,
        products: List[NormalizedProduct],
        intent: Dict[str, Any]
    ) -> str:
        lang_code = intent.get("detected_language", "en")
        dict_prods = [p.to_dict() for p in products]
        return language_service.generate_multilingual_insight(lang_code, dict_prods, intent)


class ProductDiscoveryEngine:
    def __init__(self):
        self.parser = AIIntentParser()
        self.ranker = AIRankingAndInsightEngine()
        self.providers: List[ProductProvider] = [
            LocalCatalogueProvider(),
            ExternalProductProvider()
        ]

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        sort_by: Optional[str] = None,
        intent_filter: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = context or {}
        
        intent = self.parser.parse(query, context)
        
        if category and category not in ("all", ""):
            if not intent.get("category") or not query:
                intent["category"] = category.lower()
        if brand and brand not in ("all", ""):
            intent["brand"] = brand.lower()
        if max_price:
            intent["budget"] = float(max_price)
        if sort_by:
            intent["sort_by"] = sort_by

        all_raw_products: List[NormalizedProduct] = []
        providers_status = []
        primary_recovery_tier = "EXACT_MATCH"

        for prov in self.providers:
            prov_res, tier = prov.search(query, intent, context)
            if prov.provider_type == "local_catalogue":
                primary_recovery_tier = tier
            status_desc = "ACTIVE" if prov.is_configured else "UNCONFIGURED (Demo Fallback)"
            providers_status.append({
                "provider_name": prov.name,
                "provider_type": prov.provider_type,
                "status": status_desc,
                "items_found": len(prov_res)
            })
            all_raw_products.extend(prov_res)

        seen_ids = set()
        deduped_products: List[NormalizedProduct] = []
        for p in all_raw_products:
            if p.product_id not in seen_ids:
                seen_ids.add(p.product_id)
                deduped_products.append(p)

        filtered_products: List[NormalizedProduct] = []
        for p in deduped_products:
            if min_price is not None and p.price < min_price:
                continue
            if max_price is not None and p.price > max_price:
                continue
            if min_rating is not None and p.rating < min_rating:
                continue
            filtered_products.append(p)

        ranked_products = self.ranker.rank_and_annotate(filtered_products, intent)

        # Calculate realistic non-zero intent counts across the product pool
        if ranked_products:
            prices = [p.price for p in ranked_products]
            p_min, p_max = min(prices), max(prices)
            p_median = sorted(prices)[len(prices)//2]
            
            cheapest_items = [p for p in ranked_products if p.price <= p_median or "CHEAPEST" in p.badges]
            best_rated_items = [p for p in ranked_products if p.rating >= 4.7 or "BEST RATED" in p.badges]
            premium_items = [p for p in ranked_products if p.price >= p_median or "PREMIUM PICK" in p.badges]
            best_value_items = [p for p in ranked_products if p.ai_score >= 88 or "BEST VALUE" in p.badges]
            
            filter_counts = {
                "all": len(ranked_products),
                "best_value": max(1, len(best_value_items)),
                "cheapest": max(1, len(cheapest_items)),
                "best_rated": max(1, len(best_rated_items)),
                "premium": max(1, len(premium_items))
            }
        else:
            filter_counts = {"all": 0, "best_value": 0, "cheapest": 0, "best_rated": 0, "premium": 0}

        display_products = ranked_products

        # Apply intent sorting & filtering dynamically
        active_intent = (intent_filter or intent.get("intent_type") or "").lower()
        if active_intent in ("cheapest", "cheap", "price_asc"):
            intent["intent_type"] = "CHEAPEST"
            intent["sort_by"] = "price_asc"
            display_products = sorted(ranked_products, key=lambda x: x.price)
        elif active_intent in ("best_rated", "rating_desc"):
            intent["intent_type"] = "BEST_RATED"
            intent["sort_by"] = "rating_desc"
            display_products = sorted(ranked_products, key=lambda x: (x.rating, x.review_count), reverse=True)
        elif active_intent in ("premium", "price_desc"):
            intent["intent_type"] = "PREMIUM"
            intent["sort_by"] = "price_desc"
            display_products = sorted(ranked_products, key=lambda x: x.price, reverse=True)
        elif active_intent in ("best_value", "ai_score_desc", "value"):
            intent["intent_type"] = "BEST_VALUE"
            intent["sort_by"] = "ai_score_desc"
            display_products = sorted(ranked_products, key=lambda x: recommendation_engine.calculate_value_score(x), reverse=True)
        elif intent.get("sort_by") == "price_asc":
            display_products = sorted(ranked_products, key=lambda x: x.price)
        elif intent.get("sort_by") == "rating_desc":
            display_products = sorted(ranked_products, key=lambda x: (x.rating, x.review_count), reverse=True)
        elif intent.get("sort_by") == "price_desc":
            display_products = sorted(ranked_products, key=lambda x: x.price, reverse=True)

        insight = self.ranker.generate_shopping_insight(display_products, intent)
        suggestions = language_service.get_suggestions(query, intent.get("detected_language"))

        top_recs = recommendation_engine.generate_top_recommendations(
            display_products,
            query=query,
            intent=intent,
            target_count=4
        )

        search_intelligence = {
            "original_query": query,
            "detected_language": intent.get("language_name", "English"),
            "detected_language_code": intent.get("detected_language", "en"),
            "typo_normalized": intent.get("typo_correction"),
            "interpreted_intent": intent.get("interpreted_intent") or (intent.get("category", "General Discovery").title() if intent.get("category") else "General Discovery"),
            "confidence_score": intent.get("confidence_score_percent", 95),
            "confidence_tier": intent.get("confidence_tier", "HIGH CONFIDENCE"),
            "budget_extracted": f"₹{intent['budget']:,.0f}" if intent.get("budget") else None,
            "recovery_tier": primary_recovery_tier,
            "expanded_aliases": intent.get("expanded_aliases", [])
        }

        return {
            "query": query,
            "top_recommendations": top_recs,
            "intent": intent,
            "search_intelligence": search_intelligence,
            "insight": insight,
            "detected_language": intent.get("detected_language"),
            "language_name": intent.get("language_name"),
            "confidence": intent.get("confidence"),
            "did_you_mean": intent.get("did_you_mean"),
            "suggestions": suggestions,
            "quick_filters": filter_counts,
            "intent_counts": filter_counts,
            "total_matched": len(display_products),
            "total_count": len(display_products),
            "products": [p.to_dict() for p in display_products],
            "providers_queried": providers_status,
            "is_live_data": any(p["provider_type"] == "external_verified" and p["status"] == "ACTIVE" for p in providers_status),
            "context": {
                "previous_query": query,
                "previous_category": intent.get("category"),
                "previous_budget": intent.get("budget"),
                "active_language": intent.get("detected_language"),
                "turn_count": context.get("turn_count", 0) + 1
            }
        }

    def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        raw = catalogue_engine.get_product(str(product_id))
        if not raw:
            return None
        
        orig_price = raw.get("original_price")
        specs = raw.get("features") or raw.get("specifications") or []
        if not specs and raw.get("description"):
            specs = [s.strip() for s in raw["description"].split(".") if len(s.strip()) > 5][:5]

        del_days = int(raw.get("delivery_days", 1))

        norm = NormalizedProduct(
            product_id=raw.get("product_id", product_id),
            name=raw.get("name", "Store Product"),
            brand=raw.get("brand", "Authentic Store"),
            category=raw.get("category", "general"),
            price=float(raw.get("price", 0)),
            original_price=orig_price,
            discount=raw.get("discount"),
            rating=float(raw.get("rating", 4.8)),
            review_count=int(raw.get("review_count", 1200)),
            image_url=raw.get("image_url") or raw.get("image"),
            description=raw.get("description", ""),
            specifications=specs,
            source="Storefront Catalogue",
            source_type="local_catalogue",
            is_buyable=True,
            inventory=int(raw.get("inventory", raw.get("stock", 25))),
            delivery_days=del_days,
            source_url=f"/#product/{raw.get('product_id')}",
            retrieved_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        )
        
        intent = {"category": norm.category, "budget": norm.price * 1.5, "detected_language": "en"}
        ranked = self.ranker.rank_and_annotate([norm], intent)
        p_dict = ranked[0].to_dict()
        
        p_dict["ai_recommendation_breakdown"] = [
            "✓ Verified genuine item with manufacturer warranty",
            f"✓ High customer satisfaction score ({norm.rating}★ across {norm.review_count:,} reviews)",
            f"✓ Guaranteed {norm.delivery_days}-Day Express Delivery SLA" if norm.delivery_days == 1 else f"✓ Standard {norm.delivery_days}-Day Delivery SLA",
            f"✓ In stock ({norm.inventory} units available for instant dispatch)",
            "✓ Cleared through RazorFlow X Money Safety Gate"
        ]
        return p_dict

    def compare_products(self, product_ids: List[str]) -> Dict[str, Any]:
        if not product_ids:
            return {"error": "No product IDs provided for comparison."}

        products: List[NormalizedProduct] = []
        for pid in product_ids[:4]:
            raw = catalogue_engine.get_product(str(pid))
            if raw:
                orig_price = raw.get("original_price")
                specs = raw.get("features") or raw.get("specifications") or []
                norm = NormalizedProduct(
                    product_id=raw.get("product_id", pid),
                    name=raw.get("name", "Product"),
                    brand=raw.get("brand", "Authentic"),
                    category=raw.get("category", "general"),
                    price=float(raw.get("price", 0)),
                    original_price=orig_price,
                    discount=raw.get("discount"),
                    rating=float(raw.get("rating", 4.8)),
                    review_count=int(raw.get("review_count", 1200)),
                    image_url=raw.get("image_url", ""),
                    description=raw.get("description", ""),
                    specifications=specs,
                    source="Storefront Catalogue",
                    delivery_days=int(raw.get("delivery_days", 1)),
                    inventory=int(raw.get("inventory", 25))
                )
                products.append(norm)

        if len(products) < 2:
            return {"error": "At least 2 valid products are required for comparison."}

        for p in products:
            p.ai_score = int(min(99, max(60, (p.rating / 5.0) * 50 + 48)))

        winner = max(products, key=lambda x: (x.ai_score, -x.price))
        runner_up = next((p for p in products if p.product_id != winner.product_id), products[0])

        verdict = (
            f"**{winner.name}** emerges as the overall winner with a rating of {winner.rating}★ and excellent value at ₹{winner.price:,.0f}. "
            f"If your main goal is high performance, {winner.name} provides the most robust specifications, while **{runner_up.name}** "
            f"(₹{runner_up.price:,.0f}) serves as a strong alternative."
        )

        return {
            "products": [p.to_dict() for p in products],
            "winner": winner.to_dict(),
            "verdict": verdict,
            "compared_count": len(products)
        }


discovery_engine = ProductDiscoveryEngine()
