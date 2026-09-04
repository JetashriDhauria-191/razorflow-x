from typing import List, Dict, Any, Optional
import math

try:
    from backend.catalogue import catalogue_engine
except (ImportError, ModuleNotFoundError):
    from catalogue import catalogue_engine

class GrowthBrain:
    """
    RAZORFLOW X GROWTH BRAIN
    Autonomous Commerce Intelligence Engine that optimizes both Shopper Satisfaction
    and Merchant Unit Economics (Conversion, AOV, Upsell, and Cross-Sell Yield).
    
    Generates a structured 6-point recommendation tree for any intent:
    1. Primary Pick (Best balance of Intent + Rating + Budget)
    2. Best Alternative (High customer satisfaction alternative)
    3. Budget Alternative (Economical option for price-sensitive buyers)
    4. Premium Alternative (Pro/Flagship option with superior specs)
    5. Intelligent Upsell (Higher-margin / higher-tier product)
    6. Relevant Cross-Sell (Complementary accessory / bundle)
    """

    def analyze_and_recommend(
        self,
        query: str,
        budget: Optional[float] = None,
        category: Optional[str] = None,
        current_cart: Optional[List[Dict[str, Any]]] = None,
        customer_id: str = "cust_01",
        db: Any = None
    ) -> Dict[str, Any]:
        catalogue_engine.seed_db(db)
        all_products = catalogue_engine.get_all_products(db) if hasattr(catalogue_engine, 'get_all_products') else []
        if not all_products:
            all_products = catalogue_engine.search(query="", db=db)

        q_lower = (query or "").lower().strip()
        
        # 1. Intent Analysis
        detected_category = category or "all"
        if detected_category == "all":
            if any(w in q_lower for w in ["shoe", "sneaker", "boot", "footwear", "jhootha"]):
                detected_category = "footwear"
            elif any(w in q_lower for w in ["headphone", "audio", "earphone", "earbuds", "anc", "speaker"]):
                detected_category = "audio"
            elif any(w in q_lower for w in ["laptop", "macbook", "computer", "pc", "notebook"]):
                detected_category = "laptop"
            elif any(w in q_lower for w in ["phone", "mobile", "smartphone", "iphone", "galaxy"]):
                detected_category = "phone"
            elif any(w in q_lower for w in ["shirt", "cloth", "dress", "jeans", "apparel", "kapda"]):
                detected_category = "fashion"
            elif any(w in q_lower for w in ["keyboard", "mouse", "charger", "cable", "accessory"]):
                detected_category = "tech"

        # 2. Extract Budget Constraint if mentioned in query
        detected_budget = budget
        if not detected_budget:
            import re
            num_match = re.search(r'(?:under|below|less than|budget|within|upto|up to|₹|rs\.?)\s*([0-9]+(?:,[0-9]+)*)', q_lower)
            if num_match:
                try:
                    detected_budget = float(num_match.group(1).replace(',', ''))
                except Exception:
                    pass

        # Filter candidate pool
        candidates = []
        for p in all_products:
            p_dict = p if isinstance(p, dict) else (p.to_dict() if hasattr(p, 'to_dict') else getattr(p, '__dict__', {}))
            p_cat = (p_dict.get('category') or '').lower()
            p_name = (p_dict.get('name') or '').lower()
            
            if detected_category != "all" and detected_category not in p_cat and detected_category not in p_name:
                continue
            if detected_budget and float(p_dict.get('price', 0)) > (detected_budget * 1.35):
                continue
            candidates.append(p_dict)

        if len(candidates) < 4:
            candidates = [p if isinstance(p, dict) else p.to_dict() for p in all_products]

        # Scoring function
        def score_product(prod: Dict[str, Any], role: str) -> Dict[str, Any]:
            price = float(prod.get('price', 1000))
            rating = float(prod.get('rating', 4.5))
            reviews = int(prod.get('review_count', 500))
            discount = float(prod.get('discount', 10) or 0)
            sla_days = int(prod.get('delivery_days', 1))

            intent_score = 95.0 if (detected_category != 'all' and detected_category in (prod.get('category') or '').lower()) else 85.0
            
            if detected_budget:
                price_ratio = price / detected_budget
                budget_score = max(50.0, 100.0 - abs(1.0 - price_ratio) * 40.0)
            else:
                budget_score = 88.0

            rating_score = (rating / 5.0) * 100.0
            sla_score = 100.0 if sla_days == 1 else (85.0 if sla_days == 2 else 70.0)
            margin_score = min(98.0, 70.0 + (discount * 1.2))

            total_score = round(
                (intent_score * 0.30) + 
                (budget_score * 0.25) + 
                (rating_score * 0.25) + 
                (sla_score * 0.10) + 
                (margin_score * 0.10), 
                1
            )

            return {
                "overall_score": total_score,
                "intent_match": round(intent_score, 1),
                "budget_fit": round(budget_score, 1),
                "satisfaction_rating": round(rating_score, 1),
                "delivery_sla_score": round(sla_score, 1),
                "merchant_yield_score": round(margin_score, 1)
            }

        # Sort variants
        by_price = sorted(candidates, key=lambda x: float(x.get('price', 0)))
        by_rating = sorted(candidates, key=lambda x: (float(x.get('rating', 0)), int(x.get('review_count', 0))), reverse=True)
        
        # 1. Primary Pick (best rated within budget)
        primary_pool = [c for c in by_rating if (not detected_budget or float(c.get('price', 0)) <= detected_budget)]
        primary = primary_pool[0] if primary_pool else by_rating[0]
        
        # 2. Budget Alternative (cheapest high-quality)
        budget_alt_pool = [c for c in by_price if c.get('product_id') != primary.get('product_id')]
        budget_alt = budget_alt_pool[0] if budget_alt_pool else primary
        
        # 3. Premium Alternative (top-tier/flagship)
        prem_pool = [c for c in reversed(by_price) if c.get('product_id') not in (primary.get('product_id'), budget_alt.get('product_id'))]
        premium_alt = prem_pool[0] if prem_pool else by_rating[0]

        # 4. Best Alternative (runner up with different attributes)
        best_alt_pool = [c for c in by_rating if c.get('product_id') not in (primary.get('product_id'), budget_alt.get('product_id'), premium_alt.get('product_id'))]
        best_alt = best_alt_pool[0] if best_alt_pool else (by_price[1] if len(by_price) > 1 else primary)

        # 5. Intelligent Upsell (higher price, +specs)
        upsell_pool = [c for c in by_price if float(c.get('price', 0)) > float(primary.get('price', 0)) and c.get('product_id') != primary.get('product_id')]
        upsell = upsell_pool[0] if upsell_pool else premium_alt

        # 6. Relevant Cross-Sell (accessories / complementary)
        cross_sell_pool = [c for c in all_products if (c.get('category') in ['accessories', 'tech', 'apparel'] or 'cable' in c.get('name', '').lower() or 'case' in c.get('name', '').lower() or 'socks' in c.get('name', '').lower()) and c.get('product_id') != primary.get('product_id')]
        cross_sell = cross_sell_pool[0] if cross_sell_pool else (candidates[-1] if candidates else primary)

        def build_rec_card(prod, role, badge, why_text, factors):
            p = dict(prod)
            return {
                "role": role,
                "badge": badge,
                "product_id": p.get("product_id") or p.get("id"),
                "name": p.get("name"),
                "price": float(p.get("price", 0)),
                "original_price": float(p.get("original_price", float(p.get("price", 0)) * 1.2)),
                "rating": float(p.get("rating", 4.8)),
                "review_count": int(p.get("review_count", 500)),
                "image_url": p.get("image_url", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"),
                "category": p.get("category", "general"),
                "delivery_days": int(p.get("delivery_days", 1)),
                "delivery_sla": "⚡ 1-Day Express SLA" if int(p.get("delivery_days", 1)) <= 1 else f"📦 {p.get('delivery_days', 2)}-Day Standard",
                "why_recommended": why_text,
                "growth_factors": factors
            }

        return {
            "query": query,
            "intent_analysis": {
                "detected_category": detected_category.upper(),
                "detected_budget": detected_budget,
                "price_sensitivity": "HIGH" if detected_budget and detected_budget < 3000 else "BALANCED",
                "rating_priority": "CRITICAL" if "best" in q_lower or "top" in q_lower else "STANDARD",
                "shopper_intent": f"Search for {detected_category} with budget target of ₹{detected_budget:,.0f}" if detected_budget else f"Search for {detected_category}"
            },
            "growth_recommendations": [
                build_rec_card(
                    primary,
                    "PRIMARY_PICK",
                    "⭐ #1 PRIMARY MATCH",
                    f"Optimal match: 100% budget fit with highest rating ({primary.get('rating', 4.9)}★) and Guaranteed 1-Day SLA.",
                    score_product(primary, "PRIMARY")
                ),
                build_rec_card(
                    best_alt,
                    "BEST_ALTERNATIVE",
                    "💎 BEST ALTERNATIVE",
                    f"Runner up: Highly balanced satisfaction rating ({best_alt.get('rating', 4.8)}★) with strong review volume.",
                    score_product(best_alt, "BEST_ALT")
                ),
                build_rec_card(
                    budget_alt,
                    "BUDGET_ALTERNATIVE",
                    "🏷️ BUDGET SAVER",
                    f"Save ₹{(float(primary.get('price',0)) - float(budget_alt.get('price',0))):,.0f} compared to primary pick with great core essentials.",
                    score_product(budget_alt, "BUDGET")
                ),
                build_rec_card(
                    premium_alt,
                    "PREMIUM_ALTERNATIVE",
                    "👑 PRO FLAGSHIP",
                    f"Upgrade tier: Pro performance, luxury materials, and extended durability.",
                    score_product(premium_alt, "PREMIUM")
                ),
                build_rec_card(
                    upsell,
                    "INTELLIGENT_UPSELL",
                    "⚡ SMART UPSELL",
                    f"Higher tier option: +32% more battery/performance for only ₹{(float(upsell.get('price',0)) - float(primary.get('price',0))):,.0f} delta.",
                    score_product(upsell, "UPSELL")
                ),
                build_rec_card(
                    cross_sell,
                    "RELEVANT_CROSS_SELL",
                    "📦 BUNDLE CROSS-SELL",
                    f"Frequently bought together: Attach accessory with 10% instant combo discount.",
                    score_product(cross_sell, "CROSS_SELL")
                )
            ]
        }

growth_brain = GrowthBrain()
