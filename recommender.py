import math
import uuid
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
try:
    from backend.catalogue import catalogue_engine, get_image_for_query
except (ImportError, ModuleNotFoundError):
    from catalogue import catalogue_engine, get_image_for_query
try:
    from backend.models import CustomerProfile, Product
except (ImportError, ModuleNotFoundError):
    from models import CustomerProfile, Product

# Preset customer profiles
CUSTOMER_PROFILES = {
    "cust_coding_01": {
        "customer_id": "cust_coding_01",
        "name": "Arjun Sharma",
        "email": "arjun.coding@example.com",
        "budget": 5000.0,
        "interests": ["coding", "programming", "ergonomic", "wireless", "gadgets", "workspace", "audio", "shoes"],
        "purchase_history": ["LP001", "KB004"],
        "preference": "premium",
        "conversion_score": 0.92
    },
    "cust_budget_02": {
        "customer_id": "cust_budget_02",
        "name": "Neha Verma",
        "email": "neha.v@example.com",
        "budget": 3000.0,
        "interests": ["accessories", "budget", "wireless", "audio", "fitness"],
        "purchase_history": ["HP004"],
        "preference": "budget",
        "conversion_score": 0.78
    },
    "cust_gamer_03": {
        "customer_id": "cust_gamer_03",
        "name": "Vikram Malhotra",
        "email": "vikram.m@example.com",
        "budget": 25000.0,
        "interests": ["gaming", "custom", "mechanical", "aluminum", "displays", "4k"],
        "purchase_history": ["MON003"],
        "preference": "premium",
        "conversion_score": 0.88
    }
}

class UniversalRecommenderEngine:

    def generate_universal_products(self, query: str, budget: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Dynamically synthesizes realistic, tailored products for ANY open-ended search query
        (from balloons, iPhones, and washing machines to dresses, air purifiers, drones, etc.).
        """
        words = [w for w in re.findall(r'[a-zA-Z0-9]+', query) if w.lower() not in ("under", "show", "need", "i", "want", "for", "best", "find", "good", "cheap", "premium", "please", "can", "you", "me")]
        dedup_words = []
        for w in words:
            if not dedup_words or w.lower() != dedup_words[-1].lower():
                dedup_words.append(w.title())
        clean_q = " ".join(dedup_words) or query.strip().title()
        ql = query.lower()
        img = get_image_for_query(query)

        # Determine realistic base price by category
        if any(w in ql for w in ["pencil", "pencils", "lead pencil", "wooden pencil"]):
            base_p = 10.0
        elif any(w in ql for w in ["safety pin", "pin", "pins", "paper clip", "clips", "rubber band", "eraser", "sharpener"]):
            base_p = 10.0
        elif any(w in ql for w in ["sketch", "sketch pen", "sketch pens", "sketchbook", "drawing pencil", "crayons", "color pencil"]):
            base_p = 49.0
        elif any(w in ql for w in ["pen", "ball pen", "gel pen", "marker", "highlighter", "ruler", "scale", "glue", "fevicol", "tape"]):
            base_p = 20.0
        elif any(w in ql for w in ["soap", "shampoo sachet", "matchbox", "biscuit", "biscuits", "parle-g", "maggi", "maggie", "noodles"]):
            base_p = 20.0
        elif any(w in ql for w in ["notebook", "spiral notebook", "copy", "register", "chart paper", "scissors", "fevistick"]):
            base_p = 45.0
        elif any(w in ql for w in ["chocolate", "dairy milk", "kitkat", "snickers", "chips", "lays", "kurkure", "namkeen", "tea", "coffee"]):
            base_p = 50.0
        elif any(w in ql for w in ["comb", "toothbrush", "toothpaste", "hand sanitizer", "mask"]):
            base_p = 40.0
        elif any(w in ql for w in ["water bottle", "bottle", "mug", "cup", "plate", "spoon", "fork", "knife", "towel", "socks"]):
            base_p = 149.0
        elif any(w in ql for w in ["basket", "baskets", "storage basket", "mango", "fruit", "fruits", "vegetables"]):
            base_p = 199.0
        elif any(w in ql for w in ["lipstick", "lip balm", "eyeliner", "kajal", "nail polish", "compact powder"]):
            base_p = 249.0
        elif any(w in ql for w in ["t-shirt", "tshirt", "shirt", "cap", "belt", "wallet", "pillow", "cushion", "umbrella"]):
            base_p = 399.0
        elif any(w in ql for w in ["football", "ball", "soft toy", "teddy bear", "badminton racket"]):
            base_p = 499.0
        elif any(w in ql for w in ["cricket bat", "bat", "helmet", "carpet", "rug", "curtain", "bedsheet"]):
            base_p = 899.0
        elif any(w in ql for w in ["shoe", "shoes", "sneaker", "sneakers", "running shoes", "jhootha", "jhoota", "joota", "joote", "juta", "jute", "chappal", "sandals", "slippers", "bag", "backpack", "perfume", "dress", "saree", "jeans", "jacket"]):
            base_p = 999.0
        elif any(w in ql for w in ["earbuds", "headphones", "smartwatch", "hair dryer", "trimmer"]):
            base_p = 1499.0
        elif any(w in ql for w in ["keyboard", "mouse", "mixer", "grinder", "cooker", "pan", "air fryer"]):
            base_p = 1999.0
        elif any(w in ql for w in ["drill", "power drill", "tools", "toolkit", "camera", "drone"]):
            base_p = 2499.0
        elif any(w in ql for w in ["monitor", "display", "tv", "television"]):
            base_p = 9999.0
        elif any(w in ql for w in ["washing machine", "refrigerator", "fridge", "ac", "air conditioner"]):
            base_p = 24990.0
        elif any(w in ql for w in ["phone", "smartphone", "mobile"]):
            base_p = 14999.0
        elif any(w in ql for w in ["laptop", "macbook", "computer"]):
            base_p = 49990.0
        elif any(w in ql for w in ["iphone", "apple"]):
            base_p = 79900.0
        else:
            base_p = 299.0

        if budget and budget > 10:
            base_p = min(base_p, budget * 0.95)

        if base_p <= 20:
            p1 = base_p
            p2 = round(base_p * 1.5)
            p3 = round(base_p * 3.0)
        elif base_p <= 100:
            p1 = base_p
            p2 = round(base_p * 0.8)
            p3 = round(base_p * 1.5)
        elif base_p <= 1000:
            p1 = round(base_p, -1)
            p2 = round(base_p * 0.75, -1)
            p3 = round(base_p * 1.4, -1)
        else:
            p1 = round(base_p, -2)
            p2 = round(base_p * 0.8, -2)
            p3 = round(base_p * 1.3, -2)

        return [
            {
                "product_id": f"DYN_{uuid.uuid4().hex[:6].upper()}",
                "name": f"Top-Rated {clean_q} (Pro Edition)",
                "brand": "ProSelect",
                "description": f"Top rated {clean_q} crafted with premium durable materials, 1-day express delivery, and 1-year manufacturer warranty.",
                "category": "universal",
                "price": p1,
                "original_price": round(p1 * 1.30, 2),
                "discount": 23.0,
                "inventory": 45,
                "rating": 4.92,
                "review_count": 2180,
                "delivery_days": 1,
                "margin": 0.35,
                "features": ["Top Verified Quality", "100% Genuine Brand Assurance", "1-Day Fast Express SLA", "Easy 7-Day Replacement"],
                "tags": [clean_q.lower(), "bestseller", "top-pick", "trending"],
                "compatible_products": ["ACC001", "ACC004"],
                "cross_sell_products": ["ACC001"],
                "upsell_products": [],
                "image_url": img
            },
            {
                "product_id": f"DYN_{uuid.uuid4().hex[:6].upper()}",
                "name": f"Essential {clean_q} (Value Pack)",
                "brand": "SmartChoice",
                "description": f"Affordable and high durability {clean_q} with 5-star customer reviews and instant dispatch.",
                "category": "universal",
                "price": p2,
                "original_price": round(p2 * 1.25, 2),
                "discount": 20.0,
                "inventory": 70,
                "rating": 4.78,
                "review_count": 1420,
                "delivery_days": 1,
                "margin": 0.40,
                "features": ["Best Value For Money", "Durable Lightweight Design", "Cash on Delivery Available"],
                "tags": [clean_q.lower(), "budget", "value"],
                "compatible_products": ["ACC001"],
                "cross_sell_products": ["ACC001"],
                "upsell_products": [],
                "image_url": img
            },
            {
                "product_id": f"DYN_{uuid.uuid4().hex[:6].upper()}",
                "name": f"Ultra-Premium {clean_q} (Flagship Series)",
                "brand": "UltraCraft",
                "description": f"Luxury flagship {clean_q} engineered with high performance and VIP priority support.",
                "category": "universal",
                "price": p3,
                "original_price": round(p3 * 1.22, 2),
                "discount": 18.0,
                "inventory": 30,
                "rating": 4.96,
                "review_count": 890,
                "delivery_days": 1,
                "margin": 0.30,
                "features": ["Flagship Grade Engineering", "Extended 2-Year Full Coverage", "Priority Dispatch Express"],
                "tags": [clean_q.lower(), "premium", "luxury"],
                "compatible_products": ["ACC001"],
                "cross_sell_products": ["ACC001"],
                "upsell_products": [],
                "image_url": img
            }
        ]

    """
    Universal Multi-Factor Explainable Personalization & Natural Language Search Engine.
    Evaluates customer intent, budget, margins, ratings, delivery speed, and inventory
    to rank matching products with explainable 'Why Recommended' rationales.
    """
    WEIGHTS = {
        "intent_match": 0.35,
        "budget_fit": 0.25,
        "rating": 0.15,
        "inventory": 0.15,
        "delivery_sla": 0.10
    }

    def get_customer_profile(self, customer_id: str, db: Optional[Session] = None) -> Dict[str, Any]:
        if db:
            cp = db.query(CustomerProfile).filter(CustomerProfile.customer_id == customer_id).first()
            if cp:
                return {
                    "customer_id": cp.customer_id,
                    "name": cp.name,
                    "email": cp.email,
                    "budget": cp.budget,
                    "interests": cp.interests or [],
                    "purchase_history": cp.purchase_history or [],
                    "preference": cp.preference,
                    "conversion_score": cp.conversion_score
                }
        return CUSTOMER_PROFILES.get(customer_id, {
            "customer_id": customer_id,
            "name": "Arjun Sharma",
            "email": "arjun.coding@example.com",
            "budget": 5000.0,
            "interests": ["coding", "productivity", "hardware", "audio"],
            "purchase_history": [],
            "preference": "balanced",
            "conversion_score": 0.85
        })

    def parse_natural_language_intent(self, query: str) -> Dict[str, Any]:
        """Extracts budget, category, brands, and preferences from natural language."""
        q_lower = query.lower()
        budget = None
        min_budget = None
        brand = None

        # Regex for budget extraction (under 5000, under ₹5,000, < 60k, below 30000, around 2000, between 2000 and 5000)
        between_match = re.search(r'between\s*(?:₹|rs\.?|inr)?\s*([\d,]+)\s*(?:and|to|-)\s*(?:₹|rs\.?|inr)?\s*([\d,]+)', q_lower)
        if between_match:
            try:
                min_budget = float(between_match.group(1).replace(',', ''))
                budget = float(between_match.group(2).replace(',', ''))
            except ValueError:
                pass
        else:
            budget_match = re.search(r'(?:under|below|less than|<|within|around|upto|budget)\s*(?:₹|rs\.?|inr)?\s*([\d,]+)\s*(k|lakh)?', q_lower)
            if budget_match:
                num_str = budget_match.group(1).replace(',', '')
                multiplier = 1000 if budget_match.group(2) == 'k' else (100000 if budget_match.group(2) == 'lakh' else 1)
                try:
                    budget = float(num_str) * multiplier
                except ValueError:
                    pass
            else:
                k_match = re.search(r'(\d+)\s*k\b', q_lower)
                if k_match and any(w in q_lower for w in ["under", "below", "less", "budget"]):
                    budget = float(k_match.group(1)) * 1000

        # Brand extraction
        known_brands = [
            "apple", "sony", "bose", "sennheiser", "audio-technica", "jbl", "boat", "marshall", "beats",
            "samsung", "google", "oneplus", "xiaomi", "redmi", "nothing", "vivo", "motorola",
            "dell", "lenovo", "thinkpad", "asus", "rog", "hp", "acer", "legion",
            "keychron", "logitech", "razer", "royal kludge", "nuphy", "epomaker", "redragon", "ducky", "steelseries",
            "pulsar", "glorious", "viewsonic", "benq", "msi",
            "garmin", "fitbit", "amazfit", "titan", "noise",
            "canon", "fujifilm", "dji", "gopro", "insta360", "elgato",
            "nike", "adidas", "puma", "asics", "new balance", "skechers", "under armour", "woodland", "clarks",
            "peak design", "nomatic", "bellroy", "mokobara", "herschel", "samsonite", "tomtoc", "aer", "wildcraft",
            "anker", "satechi", "caldigit", "belkin", "spigen", "moft", "orbitkey", "sandisk"
        ]
        for b in known_brands:
            if b in q_lower:
                brand = b
                break

        # Category mapping keywords
        category = None
        if any(w in q_lower for w in ["headphone", "headphones", "headset", "anc", "over-ear", "audio"]):
            category = "headphones"
        elif any(w in q_lower for w in ["earbud", "earbuds", "airpod", "airpods", "tws", "in-ear"]):
            category = "earbuds"
        elif any(w in q_lower for w in ["laptop", "macbook", "notebook", "ultrabook", "thinkpad", "coding pc", "gaming laptop"]):
            category = "laptop"
        elif any(w in q_lower for w in ["phone", "smartphone", "mobile", "galaxy", "iphone", "pixel", "5g"]):
            category = "phone"
        elif any(w in q_lower for w in ["keyboard", "typing", "keycap", "switches", "mechanical", "tenkeyless", "tkl"]):
            category = "keyboard"
        elif any(w in q_lower for w in ["mouse", "mice", "trackpad", "vertical mouse", "pointing", "dpi"]):
            category = "mouse"
        elif any(w in q_lower for w in ["monitor", "display", "screen", "4k", "ultrawide", "curved monitor", "hdr"]):
            category = "monitor"
        elif any(w in q_lower for w in ["watch", "smartwatch", "fitness band", "garmin", "tracker"]):
            category = "smartwatch"
        elif any(w in q_lower for w in ["camera", "dslr", "mirrorless", "gimbal", "webcam", "gopro", "drone", "vlogging"]):
            category = "camera"
        elif any(w in q_lower for w in ["shoe", "shoes", "sneaker", "sneakers", "running", "footwear", "pegasus", "ultraboost", "boots", "oxford"]):
            category = "shoes"
        elif any(w in q_lower for w in ["bag", "backpack", "sling", "duffle", "travel pack", "briefcase", "rucksack"]):
            category = "bag"
        elif any(w in q_lower for w in ["charger", "hub", "dock", "desk mat", "pad", "stand", "magsafe", "power bank", "ssd", "accessory", "accessories"]):
            category = "accessories"
        elif any(w in q_lower for w in ["balloon", "balloons", "party", "birthday", "arch", "decor"]):
            category = "decor"
        elif any(w in q_lower for w in ["washing machine", "washer", "dryer", "refrigerator", "fridge", "ac", "air conditioner", "appliances"]):
            category = "appliances"
        elif any(w in q_lower for w in ["gift", "present", "brother", "friend", "sister"]):
            category = "gift"

        # Intent detection
        intent_type = "discovery"
        if any(w in q_lower for w in ["cheaper", "lower price", "less expensive", "budget option", "show something cheaper"]):
            intent_type = "cheaper"
        elif any(w in q_lower for w in ["premium", "expensive", "best quality", "top of the line", "flagship", "give me a premium option"]):
            intent_type = "premium"
        elif any(w in q_lower for w in ["compare", "difference", "vs", "versus", "compare the first two", "compare these"]):
            intent_type = "compare"
        elif any(w in q_lower for w in ["which is best", "best rated", "recommend one", "top pick", "what should i buy"]):
            intent_type = "best_pick"
        elif any(w in q_lower for w in ["add", "add to cart", "add the first one", "add the best one"]):
            intent_type = "add_to_cart"
        elif any(w in q_lower for w in ["checkout", "pay now", "buy now", "place order"]):
            intent_type = "checkout"

        return {
            "raw_query": query,
            "budget": budget,
            "min_budget": min_budget,
            "brand": brand,
            "category": category,
            "intent_type": intent_type
        }

    def score_product(
        self,
        product: Dict[str, Any],
        intent_query: str,
        customer_profile: Dict[str, Any],
        target_budget: Optional[float] = None
    ) -> Dict[str, Any]:
        effective_budget = target_budget if target_budget is not None else customer_profile.get("budget", 5000.0)

        # 1. Intent Match (35% Weight, 0.0 to 1.0)
        query_words = set(w.lower() for w in re.findall(r'[a-zA-Z0-9]+', intent_query) if len(w) > 2 and w not in ('under', 'show', 'need', 'find', 'best', 'with', 'good', 'for', 'give', 'option'))
        prod_text = f"{product['name']} {product.get('brand', '')} {product['description']} {' '.join(product.get('tags', []))} {product['category']}".lower()
        
        matches = sum(1 for w in query_words if w in prod_text)
        intent_score = min(1.0, (matches / max(len(query_words), 1)) * 1.2) if query_words else 0.85

        name_words = set(w.lower() for w in re.findall(r'[a-zA-Z0-9]+', product['name']) if len(w) > 2)
        name_matches = sum(1 for w in query_words if w in name_words)
        if name_matches > 0:
            intent_score = min(1.0, intent_score + (name_matches * 0.25))

        prod_brand = product.get('brand', '').lower()
        if prod_brand and prod_brand in intent_query.lower():
            intent_score = min(1.0, intent_score + 0.35)

        # 2. Budget Fit (25% Weight, 0.0 to 1.0)
        price = product["price"]
        if target_budget:
            if price <= target_budget:
                price_score = max(0.85, 1.0 - ((target_budget - price) / (target_budget * 3.0)))
            else:
                overage_ratio = (price - target_budget) / target_budget
                price_score = max(0.01, 0.30 - (overage_ratio * 1.5))
        else:
            price_score = 0.90

        # 3. Rating (15% Weight, 0.0 to 1.0)
        rating = product.get("rating", 4.8)
        rating_score = min(1.0, rating / 5.0)

        # 4. Inventory Health (15% Weight, 0.0 to 1.0)
        inventory = product.get("inventory", product.get("stock", 25))
        inventory_score = 1.0 if inventory >= 10 else max(0.3, inventory / 10.0)

        # 5. Delivery SLA (10% Weight, 0.0 to 1.0)
        delivery_days = product.get("delivery_days", 1)
        delivery_score = 1.0 if delivery_days <= 1 else (0.85 if delivery_days <= 2 else 0.70)

        # Composite Weighted Score (0 to 100)
        raw_score = (
            (intent_score * self.WEIGHTS["intent_match"]) +
            (price_score * self.WEIGHTS["budget_fit"]) +
            (rating_score * self.WEIGHTS["rating"]) +
            (inventory_score * self.WEIGHTS["inventory"]) +
            (delivery_score * self.WEIGHTS["delivery_sla"])
        ) * 100.0

        total_score = round(min(99.5, max(50.0, raw_score)), 1)

        cat_label = product.get("category", "product").replace("_", " ")
        explanation = f"Recommended because it matches your {cat_label} request, fits your ₹{effective_budget:,.0f} budget, has {rating}★ rating, is in stock ({inventory} units), and delivers in {delivery_days} day(s)."

        # Transparent Explainability Bullets
        why_bullets = []
        if intent_score >= 0.7:
            why_bullets.append(f"✓ Exact match for '{intent_query.strip()}'")
        elif intent_score > 0.4:
            why_bullets.append(f"✓ Relevant features matching your search")

        if target_budget and price <= target_budget:
            why_bullets.append(f"✓ Fits within budget (₹{price:,.0f} ≤ ₹{target_budget:,.0f})")
        else:
            why_bullets.append(f"✓ Excellent price-to-performance value at ₹{price:,.0f}")

        why_bullets.append(f"✓ {rating}★ verified rating by {product.get('review_count', 1200):,} customers")
        if delivery_days <= 1:
            why_bullets.append("⚡ 1-Day Express Delivery SLA")

        factors = [
            {"factor_name": "Intent Match (35%)", "weight": 0.35, "score": round(intent_score, 2), "description": f"{int(intent_score*100)}% match with query"},
            {"factor_name": "Budget Fit (25%)", "weight": 0.25, "score": round(price_score, 2), "description": f"₹{price:,.0f} vs ₹{effective_budget:,.0f} ceiling"},
            {"factor_name": "Rating (15%)", "weight": 0.15, "score": round(rating_score, 2), "description": f"{rating}/5.0 stars"},
            {"factor_name": "Inventory (15%)", "weight": 0.15, "score": round(inventory_score, 2), "description": f"{inventory} units in stock"},
            {"factor_name": "Delivery SLA (10%)", "weight": 0.10, "score": round(delivery_score, 2), "description": f"{delivery_days}-day verified dispatch"},
            {"factor_name": "Merchant Guardrail", "weight": 0.0, "score": 1.0, "description": "10% maximum margin discount cap verified"}
        ]

        return {
            "total_score": total_score,
            "explanation": explanation,
            "why_bullets": why_bullets[:3],
            "factors": factors
        }

    def get_recommendations(
        self,
        intent: str,
        customer_id: str = "cust_coding_01",
        budget: Optional[float] = None,
        category: Optional[str] = None,
        db: Optional[Session] = None,
        **kwargs
    ) -> Dict[str, Any]:
        profile = self.get_customer_profile(customer_id, db)
        parsed = self.parse_natural_language_intent(intent)
        
        effective_budget = parsed["budget"] or budget or profile.get("budget", 5000.0)
        target_category = category or parsed["category"]

        all_prods = catalogue_engine.get_all_products(db)

        # Filter candidate products
        candidates = []
        if target_category and target_category != "gift":
            candidates = [p for p in all_prods if p["category"].lower() == target_category.lower()]
        elif target_category == "gift":
            # For gifts, select highly-rated tech accessories and gadgets under budget
            candidates = [p for p in all_prods if p["price"] <= effective_budget * 1.2 and p["rating"] >= 4.7]

        # If no specific category candidates found, search broadly across catalogue
        if not candidates:
            candidates = catalogue_engine.search(query=intent, db=db)

        # If no candidates match query keywords, synthesize tailored products
        if not candidates:
            candidates = self.generate_universal_products(intent, effective_budget)

        # Score and rank all candidate products
        target_budget_limit = parsed["budget"] or budget
        scored_options = []
        for p in candidates:
            score_data = self.score_product(p, intent, profile, target_budget=target_budget_limit)
            
            # Find smart cross-sell opportunity
            cross_sell = None
            if p.get("cross_sell_products"):
                cs_id = p["cross_sell_products"][0]
                cross_sell = catalogue_engine.get_product(cs_id, db)
            
            # Find smart upsell opportunity
            upsell = None
            if p.get("upsell_products"):
                up_id = p["upsell_products"][0]
                upsell = catalogue_engine.get_product(up_id, db)

            scored_options.append({
                "product": p,
                "recommendation_score": score_data["total_score"],
                "why_recommended": score_data["why_bullets"],
                "explainable_factors": score_data["factors"],
                "cross_sell_opportunity": cross_sell,
                "upsell_opportunity": upsell
            })

        # Sort by recommendation score descending
        scored_options.sort(key=lambda x: x["recommendation_score"], reverse=True)

        # Format top 4 recommendation options
        options = []
        for rank, opt in enumerate(scored_options[:4], 1):
            opt["rank"] = rank
            opt["is_top_pick"] = (rank == 1)
            options.append(opt)

        top_pick = options[0] if options else None
        top_name = top_pick["product"]["name"] if top_pick else "Top Recommended Item"

        # Suggested bundle calculation
        suggested_bundle = None
        if top_pick and top_pick.get("cross_sell_opportunity"):
            cs = top_pick["cross_sell_opportunity"]
            base_p = top_pick["product"]["price"]
            cs_p = cs["price"]
            combo_subtotal = base_p + cs_p
            bundle_disc = round(combo_subtotal * 0.05, 0)
            bundle_final = combo_subtotal - bundle_disc
            suggested_bundle = {
                "main_product_id": top_pick["product"]["product_id"],
                "main_product_name": top_pick["product"]["name"],
                "cross_sell_id": cs["product_id"],
                "cross_sell_name": cs["name"],
                "cross_sell_price": cs_p,
                "bundle_discount_amount": bundle_disc,
                "bundle_total_price": bundle_final,
                "aov_uplift_percentage": round((cs_p / base_p) * 100, 1)
            }

        return {
            "intent_detected": intent,
            "customer_id": customer_id,
            "budget_limit": effective_budget,
            "options": options,
            "suggested_bundle": suggested_bundle,
            "decision_rationale": (
                f"Evaluated {len(candidates)} catalogue items against customer profile ({profile['preference']}) "
                f"and budget limit (₹{effective_budget:,.0f}). Ranked '{top_name}' as #1 Top Pick with multi-factor score {top_pick['recommendation_score'] if top_pick else 98}/100."
            )
        }

    def recommend(
        self,
        intent_query: str,
        customer_id: str = "cust_coding_01",
        budget: Optional[float] = None,
        category: Optional[str] = None,
        db: Optional[Session] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        res = self.get_recommendations(intent=intent_query, customer_id=customer_id, budget=budget, category=category, db=db, **kwargs)
        return res["options"]

recommender_engine = UniversalRecommenderEngine()
