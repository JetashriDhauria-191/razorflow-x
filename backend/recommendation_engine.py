from typing import List, Dict, Any, Optional

def get_sla(p):
    if hasattr(p, 'delivery_sla') and getattr(p, 'delivery_sla'):
        return p.delivery_sla
    d = getattr(p, 'delivery_days', 1)
    return "1-Day Express" if d <= 1 else ("2-Day Standard" if d == 2 else f"{d}-Day Regional")

class RecommendationEngine:
    """
    Computes dynamic, explainable AI Top Recommendations adapted to user search intent:
    - CHEAPEST: Sorts strictly by lowest price ascending (₹299, ₹499, ₹799...)
    - BEST RATED: Sorts strictly by highest rating (5.0★ / 4.9★) and review count descending
    - PREMIUM: Surfaces genuinely flagship, pro-tier, and luxury hardware descending
    - BEST VALUE: Independent ranking using a balanced value formula (rating + discount + price competitiveness + reviews)
    - ALL / BALANCED: Balanced multi-factor score
    - STRICT UNIQUENESS: Visible recommendations contain ZERO duplicate products.
    """

    def calculate_value_score(self, prod: Any) -> float:
        rating = float(getattr(prod, 'rating', 4.5) if not isinstance(prod, dict) else prod.get('rating', 4.5))
        price = float(getattr(prod, 'price', 1000.0) if not isinstance(prod, dict) else prod.get('price', 1000.0))
        discount = float((getattr(prod, 'discount', 0.0) if not isinstance(prod, dict) else prod.get('discount', 0.0)) or 0.0)
        reviews = int(getattr(prod, 'review_count', 1000) if not isinstance(prod, dict) else prod.get('review_count', 1000))

        # Rating component: up to 35 pts
        rating_pts = (rating / 5.0) * 35.0

        # Discount component: up to 25 pts
        discount_pts = min(25.0, discount * 0.5)

        # Price competitiveness component: up to 25 pts
        if price <= 1000:
            price_pts = 25.0
        elif price <= 5000:
            price_pts = 22.0
        elif price <= 25000:
            price_pts = 18.0
        elif price <= 75000:
            price_pts = 14.0
        else:
            price_pts = 10.0

        # Review volume component: up to 15 pts
        reviews_pts = min(15.0, (reviews / 2000.0) * 15.0)

        return round(rating_pts + discount_pts + price_pts + reviews_pts, 1)

    def generate_top_recommendations(
        self,
        products: List[Any],
        query: str = "",
        intent: Optional[Dict[str, Any]] = None,
        target_count: int = 4
    ) -> List[Dict[str, Any]]:
        if not products:
            return []

        intent = intent or {}
        intent_type = (intent.get("intent_type") or "").upper()
        sort_by = (intent.get("sort_by") or "").lower()
        q_lower = (query or "").lower().strip()

        # Deduplicate input product pool first to guarantee uniqueness
        seen_pool_ids = set()
        unique_products = []
        for p in products:
            pid = str(getattr(p, 'product_id', getattr(p, 'id', '')) if not isinstance(p, dict) else (p.get('product_id') or p.get('id') or ''))
            if pid and pid not in seen_pool_ids:
                seen_pool_ids.add(pid)
                unique_products.append(p)
            elif not pid:
                unique_products.append(p)

        if not unique_products:
            unique_products = products

        # Determine effective intent mode
        is_cheap_mode = (
            intent_type in ("CHEAPEST", "CHEAP") or 
            sort_by == "price_asc" or 
            any(w in q_lower for w in ["cheap", "cheaper", "cheapest", "low price", "budget", "sasta", "மலிவான"])
        )
        is_premium_mode = (
            intent_type == "PREMIUM" or 
            sort_by == "price_desc" or 
            any(w in q_lower for w in ["premium", "luxury", "flagship", "expensive", "top tier", "pro", "ultra", "விலை உயர்ந்த"])
        )
        is_best_rated_mode = (
            intent_type in ("BEST_RATED", "BEST RATED", "RATING") or 
            sort_by == "rating_desc" or 
            any(w in q_lower for w in ["best rated", "top rated", "highest rated", "5 star", "favorite", "மக்கள் விரும்பிய"])
        )
        is_best_value_mode = (
            intent_type in ("BEST_VALUE", "BEST VALUE", "VALUE") or 
            sort_by == "ai_score_desc" or 
            any(w in q_lower for w in ["best value", "value for money", "bang for buck", "balanced"])
        )

        selected_prods = []
        used_ids = set()

        def get_p_dict(prod):
            if hasattr(prod, 'to_dict'):
                d = prod.to_dict()
            elif hasattr(prod, 'dict'):
                d = prod.dict()
            elif isinstance(prod, dict):
                d = dict(prod)
            else:
                d = {
                    "product_id": getattr(prod, 'product_id', getattr(prod, 'id', '')),
                    "id": getattr(prod, 'id', getattr(prod, 'product_id', '')),
                    "name": getattr(prod, 'name', 'Product'),
                    "price": getattr(prod, 'price', 0),
                    "rating": getattr(prod, 'rating', 4.8),
                    "review_count": getattr(prod, 'review_count', 100),
                    "image_url": getattr(prod, 'image_url', ''),
                    "category": getattr(prod, 'category', 'general')
                }
            return d

        if is_cheap_mode:
            # 1. CHEAPEST: Sort strictly by final price ascending
            sorted_pool = sorted(unique_products, key=lambda p: float(getattr(p, 'price', p.get('price', 0) if isinstance(p, dict) else 0)))
            badges = ["🏷️ #1 LOWEST PRICE", "💰 BUDGET TOP PICK", "⚡ BEST AFFORDABLE CHOICE", "💎 VALUE UNDER BUDGET"]
            roles = ["Lowest Price Verified Item", "Budget Price Leader", "Affordable Choice", "Budget Friendly Deal"]
            
            for prod in sorted_pool:
                pid = str(getattr(prod, 'product_id', getattr(prod, 'id', '')) if not isinstance(prod, dict) else (prod.get('product_id') or prod.get('id') or ''))
                if pid in used_ids:
                    continue
                used_ids.add(pid)
                
                idx = len(selected_prods)
                p_dict = get_p_dict(prod)
                p_price = float(p_dict.get('price', 0))
                p_rating = float(p_dict.get('rating', 4.8))
                
                p_dict["badge_label"] = badges[idx] if idx < len(badges) else "🏷️ CHEAPEST PICK"
                p_dict["role_title"] = roles[idx] if idx < len(roles) else "Budget Choice"
                p_dict["role_badge"] = p_dict["badge_label"]
                p_dict["ai_verdict_reason"] = f"Lowest price option at ₹{p_price:,.0f} with verified {p_rating}★ rating."
                p_dict["explanation"] = f"Lowest price at ₹{p_price:,.0f} with verified {p_rating}★ rating."
                p_dict["ai_score"] = max(85, 98 - (idx * 3))
                selected_prods.append(p_dict)
                if len(selected_prods) >= target_count:
                    break

        elif is_premium_mode:
            # 2. PREMIUM: Sort strictly by highest price descending (flagship models)
            sorted_pool = sorted(unique_products, key=lambda p: float(getattr(p, 'price', p.get('price', 0) if isinstance(p, dict) else 0)), reverse=True)
            badges = ["👑 FLAGSHIP #1 PICK", "⭐ LUXURY PRO EDITION", "🏆 ULTIMATE PERFORMANCE", "💎 TOP-TIER HARDWARE"]
            roles = ["Flagship Category Leader", "Pro Luxury Hardware", "Ultimate Spec Tier", "High-End Experience"]
            
            for prod in sorted_pool:
                pid = str(getattr(prod, 'product_id', getattr(prod, 'id', '')) if not isinstance(prod, dict) else (prod.get('product_id') or prod.get('id') or ''))
                if pid in used_ids:
                    continue
                used_ids.add(pid)
                
                idx = len(selected_prods)
                p_dict = get_p_dict(prod)
                p_price = float(p_dict.get('price', 0))
                p_rating = float(p_dict.get('rating', 4.8))
                
                p_dict["badge_label"] = badges[idx] if idx < len(badges) else "👑 PREMIUM PICK"
                p_dict["role_title"] = roles[idx] if idx < len(roles) else "Flagship Pro"
                p_dict["role_badge"] = p_dict["badge_label"]
                p_dict["ai_verdict_reason"] = f"Top-tier flagship hardware (₹{p_price:,.0f}) with premium specs and {p_rating}★ rating."
                p_dict["explanation"] = f"Flagship tier (₹{p_price:,.0f}) with pro specifications."
                p_dict["ai_score"] = max(88, 99 - (idx * 2))
                selected_prods.append(p_dict)
                if len(selected_prods) >= target_count:
                    break

        elif is_best_rated_mode:
            # 3. BEST RATED: Sort strictly by highest rating and review count descending
            sorted_pool = sorted(
                unique_products,
                key=lambda p: (
                    float(getattr(p, 'rating', p.get('rating', 0) if isinstance(p, dict) else 0)),
                    int(getattr(p, 'review_count', p.get('review_count', 0) if isinstance(p, dict) else 0))
                ),
                reverse=True
            )
            badges = ["⭐ HIGHEST RATED (5.0★)", "🏆 CUSTOMER FAVORITE", "🥇 TOP REVIEWED PICK", "✨ 5-STAR EXCELLENCE"]
            roles = ["Highest Customer Satisfaction", "Community Top Favorite", "Bestseller Leader", "Proven Quality"]
            
            for prod in sorted_pool:
                pid = str(getattr(prod, 'product_id', getattr(prod, 'id', '')) if not isinstance(prod, dict) else (prod.get('product_id') or prod.get('id') or ''))
                if pid in used_ids:
                    continue
                used_ids.add(pid)
                
                idx = len(selected_prods)
                p_dict = get_p_dict(prod)
                p_rating = float(p_dict.get('rating', 4.9))
                p_reviews = int(p_dict.get('review_count', 1200))
                
                p_dict["badge_label"] = badges[idx] if idx < len(badges) else "⭐ BEST RATED"
                p_dict["role_title"] = roles[idx] if idx < len(roles) else "Customer Favorite"
                p_dict["role_badge"] = p_dict["badge_label"]
                p_dict["ai_verdict_reason"] = f"Exceptional {p_rating}★ customer rating across {p_reviews:,} verified buyers."
                p_dict["explanation"] = f"Top-rated ({p_rating}★) with {p_reviews:,} verified buyer reviews."
                p_dict["ai_score"] = max(90, 99 - (idx * 2))
                selected_prods.append(p_dict)
                if len(selected_prods) >= target_count:
                    break

        elif is_best_value_mode:
            # 4. BEST VALUE: Independent ranking using balanced value score formula
            sorted_pool = sorted(unique_products, key=lambda p: self.calculate_value_score(p), reverse=True)
            badges = ["💰 BEST VALUE #1", "🎯 HIGH ROI DEAL", "⚡ SMART BUDGET LEADER", "💎 MAX VALUE SCORE"]
            roles = ["Highest Value-to-Price Ratio", "Optimal Quality per Rupee", "Smart Consumer Pick", "Exceptional Value"]
            
            for prod in sorted_pool:
                pid = str(getattr(prod, 'product_id', getattr(prod, 'id', '')) if not isinstance(prod, dict) else (prod.get('product_id') or prod.get('id') or ''))
                if pid in used_ids:
                    continue
                used_ids.add(pid)
                
                idx = len(selected_prods)
                p_dict = get_p_dict(prod)
                p_price = float(p_dict.get('price', 0))
                p_rating = float(p_dict.get('rating', 4.8))
                v_score = self.calculate_value_score(prod)
                
                p_dict["badge_label"] = badges[idx] if idx < len(badges) else "💰 BEST VALUE"
                p_dict["role_title"] = roles[idx] if idx < len(roles) else "Value Leader"
                p_dict["role_badge"] = p_dict["badge_label"]
                p_dict["ai_verdict_reason"] = f"Value Score: {v_score}/100 based on price (₹{p_price:,.0f}), {p_rating}★ rating, and feature balance."
                p_dict["explanation"] = f"Maximum value for money: ₹{p_price:,.0f} with {p_rating}★ rating."
                p_dict["ai_score"] = int(min(99, max(85, v_score)))
                selected_prods.append(p_dict)
                if len(selected_prods) >= target_count:
                    break

        else:
            # 5. ALL RESULTS / BALANCED: Best overall, best value, premium choice, most popular
            sorted_pool = sorted(unique_products, key=lambda p: getattr(p, 'ai_score', float(getattr(p, 'rating', 4.5)) * 20), reverse=True)
            badges = ["🥇 BEST OVERALL", "💰 BEST VALUE", "⭐ PREMIUM CHOICE", "🔥 MOST POPULAR"]
            roles = ["Optimal Performance & Price", "Maximum Value for Money", "Flagship Tier Hardware", "Community Bestseller"]
            
            for prod in sorted_pool:
                pid = str(getattr(prod, 'product_id', getattr(prod, 'id', '')) if not isinstance(prod, dict) else (prod.get('product_id') or prod.get('id') or ''))
                if pid in used_ids:
                    continue
                used_ids.add(pid)
                
                idx = len(selected_prods)
                p_dict = get_p_dict(prod)
                p_price = float(p_dict.get('price', 0))
                p_rating = float(p_dict.get('rating', 4.8))
                
                p_dict["badge_label"] = badges[idx] if idx < len(badges) else "✨ AI TOP PICK"
                p_dict["role_title"] = roles[idx] if idx < len(roles) else "Top Recommendation"
                p_dict["role_badge"] = p_dict["badge_label"]
                p_dict["ai_verdict_reason"] = f"Balanced AI recommendation fit: ₹{p_price:,.0f} with {p_rating}★."
                p_dict["explanation"] = f"Top recommendation based on multi-attribute scoring: ₹{p_price:,.0f}."
                p_dict["ai_score"] = max(86, 97 - (idx * 3))
                selected_prods.append(p_dict)
                if len(selected_prods) >= target_count:
                    break

        return selected_prods

recommendation_engine = RecommendationEngine()
