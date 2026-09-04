import re
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
try:
    from backend.catalogue import catalogue_engine
except (ImportError, ModuleNotFoundError):
    from catalogue import catalogue_engine
try:
    from backend.recommender import recommender_engine
except (ImportError, ModuleNotFoundError):
    from recommender import recommender_engine
try:
    from backend.growth_engine import growth_engine
except (ImportError, ModuleNotFoundError):
    from growth_engine import growth_engine
try:
    from backend.policy_gate import policy_gate
except (ImportError, ModuleNotFoundError):
    from policy_gate import policy_gate
try:
    from backend.agent_orchestrator import agent_toolbox
except (ImportError, ModuleNotFoundError):
    from agent_orchestrator import agent_toolbox
try:
    from backend.audit_trace import audit_logger
except (ImportError, ModuleNotFoundError):
    from audit_trace import audit_logger

class AgenticCheckoutEngine:
    """
    Conversational & Voice-Enabled AI Checkout Agent.
    Transforms natural language & voice intent into explainable, policy-gated Razorpay transactions
    across multiple product categories (Keyboards, Mice, Audio/Headphones, Docks/Accessories, Monitors, Shoes, etc.).
    """

    def parse_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower().strip()
        
        # Extract budget (e.g., under 2000, below 3000, for 1500, budget 2500, < 5000)
        budget = None
        budget_match = re.search(r'(?:under|below|less than|within|budget of|\<|\₹|\rs\.?)\s*([0-9]+[0-9,]*)', msg_lower)
        if budget_match:
            try:
                budget = float(budget_match.group(1).replace(',', ''))
            except ValueError:
                budget = None

        # Category detection across all major categories        
        category = "all"
        if any(w in msg_lower for w in ["keyboard", "keys", "mechanical", "switch", "keycaps", "typing", "कीबोर्ड", "விசைப்பலகை", "కీబోర్డ్", "teclado", "clavier"]):
            category = "keyboard"
        elif any(w in msg_lower for w in ["mouse", "mice", "pointer", "vertical", "trackball", "dpi", "माउस", "சுட்டி", "మౌస్", "ratón", "souris"]):
            category = "mouse"
        elif any(w in msg_lower for w in ["headphone", "headphones", "headset", "audio", "mic", "microphone", "earbuds", "anc", "sound", "spatial", "airpod", "airpods", "हेडफोन", "இயர்போன்", "హెడ్‌ఫోన్లు", "auriculares", "écouteurs", "kopfhörer"]):
            category = "headphones"
        elif any(w in msg_lower for w in ["laptop", "macbook", "notebook", "ultrabook", "thinkpad", "coding pc", "लैपटॉप", "மடிக்கணினி", "లాప్‌టాప్", "portátil", "ordinateur"]):
            category = "laptop"
        elif any(w in msg_lower for w in ["iphone", "phone", "smartphone", "mobile", "galaxy", "pixel", "5g", "फोन", "मोबाइल", "தொலைபேசி", "ఫోన్", "teléfono", "téléphone", "handy"]):
            category = "phone"
        elif any(w in msg_lower for w in ["balloon", "balloons", "party", "birthday", "decor", "celebration", "lights", "सजावट", "दीया", "decoración"]):
            category = "decor"
        elif any(w in msg_lower for w in ["washing machine", "washer", "dryer", "refrigerator", "fridge", "ac", "air conditioner", "appliances", "वाशिंग मशीन", "फ्रिज", "குளிரூட்டி", "lavadora", "frigorífico"]):
            category = "appliances"
        elif any(w in msg_lower for w in ["shirt", "tshirt", "t-shirt", "dress", "saree", "kurti", "hoodie", "jacket", "jeans", "fashion", "apparel", "clothing", "कपड़े", "साड़ी", "सूट", "சட்டை", "சேலை", "చొక్కா", "ropa", "vêtements", "kleidung"]):
            category = "fashion"
        elif any(w in msg_lower for w in ["air fryer", "mixer", "grinder", "cookware", "kitchen", "रसोई", "சமையல்", "cocina"]):
            category = "kitchen"
        elif any(w in msg_lower for w in ["hair dryer", "trimmer", "grooming", "perfume", "beauty", "lipstick", "makeup", "लिपस्टिक", "मेकअप", "perfume", "belleza", "beauté"]):
            category = "beauty"
        elif any(w in msg_lower for w in ["lego", "toy", "toys", "kids", "खिलौने", "பொம்மை", "బొమ్మలు", "juguetes", "jouets"]):
            category = "toys"
        elif any(w in msg_lower for w in ["chair", "office chair", "sofa", "furniture", "desk", "कुर्सी", "सोफा", "நாற்காலி", "కుర్చీ", "silla", "chaise"]):
            category = "furniture"
        elif any(w in msg_lower for w in ["monitor", "display", "screen", "ultrawide", "4k", "curved", "स्क्रीन", "திரை", "pantalla", "écran"]):
            category = "monitor"
        elif any(w in msg_lower for w in ["watch", "smartwatch", "fitness", "garmin", "band", "ghadi", "घड़ी", "கடிகாரம்", "గడియారం", "reloj", "montre", "uhr"]):
            category = "smartwatch"
        elif any(w in msg_lower for w in ["camera", "dslr", "mirrorless", "gimbal", "webcam", "gopro", "drone", "कैमरा", "கேமரா", "కెమెరా", "cámara", "appareil photo"]):
            category = "camera"
        elif any(w in msg_lower for w in ["shoe", "shoes", "sneaker", "sneakers", "running", "pegasus", "ultraboost", "jhootha", "jhoota", "joota", "joote", "juta", "jute", "chappal", "sandals", "mojdi", "footwear", "bata", "जूते", "जूता", "காலணி", "ஷூ", "బూట్లు", "zapatos", "chaussures", "schuhe"]):
            category = "shoes"
        elif any(w in msg_lower for w in ["bag", "backpack", "sling", "duffle", "travel pack", "बैग", "बस्ता", "பை", "சஞ்சி", "mochila", "sac", "tasche"]):
            category = "bag"
        elif any(w in msg_lower for w in ["mat", "pad", "deskmat", "hub", "dock", "usbc", "usb-c", "charger", "gan", "wrist rest", "sd card", "accessory", "accessories"]):
            category = "accessories"

        # Language Identification
        detected_language = "English (Global)"
        if re.search(r'[\u0900-\u097F]', message) or any(w in msg_lower for w in ["jhootha", "jhoota", "joota", "joote", "juta", "kapda", "kapde", "karo", "chahiye", "dikhao", "batao", "sasta", "accha", "kalam", "kitab", "paisa", "rupaye", "kholna", "khol"]):
            detected_language = "Hindi / Hinglish (हिंदी)"
        elif re.search(r'[\u0B80-\u0BFF]', message) or any(w in msg_lower for w in ["vendum", "kattu", "vaanga", "panam", "pudhu"]):
            detected_language = "Tamil (தமிழ்)"
        elif re.search(r'[\u0C00-\u0C7F]', message) or any(w in msg_lower for w in ["kavali", "chupinchu", "konandi", "dabbulu"]):
            detected_language = "Telugu (తెలుగు)"
        elif re.search(r'[\u0C80-\u0CFF]', message):
            detected_language = "Kannada (ಕನ್ನಡ)"
        elif re.search(r'[\u0D00-\u0D7F]', message):
            detected_language = "Malayalam (മലയാളം)"
        elif re.search(r'[\u0980-\u09FF]', message):
            detected_language = "Bengali (বাংলা)"
        elif any(w in msg_lower for w in ["hola", "zapatos", "camisa", "comprar", "cuanto", "bueno", "barato", "gracias"]):
            detected_language = "Spanish (Español)"
        elif any(w in msg_lower for w in ["bonjour", "chaussures", "acheter", "combien", "merci"]):
            detected_language = "French (Français)"
        elif any(w in msg_lower for w in ["hallo", "schuhe", "kaufen", "billig", "danke"]):
            detected_language = "German (Deutsch)"

        # Action intent (priority: ADD_CROSS_SELL -> DECLINE_CROSS_SELL -> CHECKOUT_CONFIRM -> COMPARE -> CHEAPER -> PREMIUM -> BEST_PICK -> SUGGEST_USEFUL -> DISCOVERY)
        if any(w in msg_lower for w in [
            "add cross-sell", "add cross sell", "add combo", "yes add", "add mouse", "add pad", "add hub",
            "add mic", "add dock", "add to combo", "add this", "include cross-sell", "include accessory", "add recommended",
            "भी जोड़ो", "ಕಾಂಬೊ ಸೇರಿಸಿ"
        ]):
            action_intent = "ADD_CROSS_SELL"
        elif any(w in msg_lower for w in ["skip", "no cross-sell", "no thank", "only this", "just this", "without accessory", "नहीं चाहिए", "வேண்டாம்"]):
            action_intent = "DECLINE_CROSS_SELL"
        elif any(w in msg_lower for w in ["compare", "difference", "vs", "versus", "compare the first two", "compare these", "तुलना करो", "ஒப்பிடு", "పోల్చండి"]):
            action_intent = "COMPARE"
        elif any(w in msg_lower for w in ["cheaper", "lower price", "less expensive", "budget option", "show something cheaper", "find cheaper", "सस्ता", "कम दाम", "குறைந்த விலை", "తక్కువ ధర", "barato", "moins cher"]):
            action_intent = "CHEAPER"
        elif any(w in msg_lower for w in ["premium", "expensive", "best quality", "flagship", "give me a premium option", "top tier", "महंगा", "बेस्ट क्वालिटी", "cara"]):
            action_intent = "PREMIUM"
        elif any(w in msg_lower for w in ["which is best", "what should i buy", "recommend one", "top pick", "best option", "कौन सा अच्छा है", "எது சிறந்தது"]):
            action_intent = "BEST_PICK"
        elif any(w in msg_lower for w in ["suggest something useful", "useful with it", "accessory with it", "what goes with this", "suggest bundle"]):
            action_intent = "SUGGEST_USEFUL"
        elif any(w in msg_lower for w in ["add the first one", "add first one", "add the best one", "add option 1", "add first"]):
            action_intent = "ADD_FIRST"
        elif any(w in msg_lower for w in ["buy", "checkout", "create order", "proceed", "pay", "order now", "confirm", "yes", "place order", "choose option", "select option", "i choose", "add to cart", "खरीदो", "भुगतान करो", "வாங்க", "కొనండి", "comprar", "acheter"]):
            action_intent = "CHECKOUT_CONFIRM"
        else:
            action_intent = "DISCOVERY"

        return {
            "query": message,
            "category": category,
            "budget": budget,
            "detected_language": detected_language,
            "action_intent": action_intent,
            "keywords": [w for w in msg_lower.split() if len(w) > 2]
        }

    def process_customer_turn(
        self,
        message: str,
        session_id: Optional[str] = None,
        customer_id: str = "cust_coding_01",
        current_cart: Optional[List[Dict[str, Any]]] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        session_id = session_id or f"sess_{uuid.uuid4().hex[:8]}"
        parsed = self.parse_intent(message)
        action_intent = parsed["action_intent"]
        current_cart = current_cart or []

        # 1. Log User Intent in Audit Trace
        audit_logger.log_step(
            session_id=session_id,
            stage="USER_INTENT_DETECTED",
            action_name="PARSE_INTENT",
            decision_explanation=f"Customer intent detected: '{action_intent}' for category '{parsed['category']}' with budget constraint: ₹{parsed['budget'] or 'Flexible'}.",
            policy_status="PASSED",
            money_amount=parsed["budget"],
            metadata={"raw_message": message, "parsed": parsed},
            db=db
        )

        # SCENARIO A: Customer confirms / proceeds to checkout
        if action_intent == "CHECKOUT_CONFIRM":
            if not current_cart:
                # Default to top matched product if cart was empty
                top_match = catalogue_engine.search(query=message, category=parsed["category"] if parsed["category"] != "all" else None, db=db)
                selected = top_match[0] if top_match else catalogue_engine.get_product("HP001", db) or catalogue_engine.get_product("KB001", db)
                current_cart = [{"product_id": selected["product_id"], "name": selected["name"], "price": selected["price"], "quantity": 1}]

            cart_total = sum(i["price"] * i.get("quantity", 1) for i in current_cart)
            product_ids = [i["product_id"] for i in current_cart]

            # Run Money Action Safety Gate
            policy_eval = policy_gate.evaluate_money_action(
                action_type="ORDER_CREATION",
                amount=cart_total,
                discount_percentage=0.0,
                product_ids=product_ids,
                customer_confirmed=True,
                session_id=session_id,
                db=db
            )

            audit_logger.log_step(
                session_id=session_id,
                stage="POLICY_SAFETY_GATE",
                action_name="EVALUATE_POLICY",
                decision_explanation=f"Money Action Safety Gate evaluated: {policy_eval['status']}. {policy_eval['reason']}",
                policy_status=policy_eval["status"],
                money_amount=cart_total,
                metadata={"rules": policy_eval["rules_evaluated"]},
                db=db
            )

            if not policy_eval["is_allowed"]:
                return {
                    "session_id": session_id,
                    "message": f"⚠️ **Action Blocked by Merchant Safety Policy**:\n\n{policy_eval['reason']}",
                    "intent": action_intent,
                    "policy_status": "BLOCKED",
                    "policy_details": policy_eval,
                    "ready_for_checkout": False,
                    "recommendations": []
                }

            # Create Razorpay Test Order
            order_res = agent_toolbox.create_razorpay_order(
                amount=cart_total,
                session_id=session_id,
                is_ai_assisted=len(current_cart) > 1,
                baseline_amount=current_cart[0]["price"] if current_cart else cart_total,
                db=db
            )

            return {
                "session_id": session_id,
                "message": (
                    f"✅ **Money Safety Gate Passed**! Bounded Razorpay Test Order initialized.\n\n"
                    f"📦 **Order ID**: `{order_res.get('order_id')}`\n"
                    f"💰 **Total Amount**: **₹{cart_total:,.2f}**\n"
                    f"🔒 **Policy Checks**: All 8 Risk & Safety rules verified.\n\n"
                    f"Click **[ Complete Razorpay Payment ]** to verify test payment."
                ),
                "intent": action_intent,
                "policy_status": "PASSED",
                "ready_for_checkout": True,
                "order": order_res,
                "razorpay_order_payload": order_res,
                "cart": {
                    "session_id": session_id,
                    "customer_id": customer_id,
                    "items": current_cart,
                    "base_total": cart_total,
                    "discount_total": 0.0,
                    "final_total": cart_total,
                    "is_bundled": len(current_cart) > 1,
                    "status": "ORDER_CREATED"
                },
                "recommendations": []
            }

        # SCENARIO B: Customer accepts cross-sell
        elif action_intent == "ADD_CROSS_SELL":
            primary_item = current_cart[0] if current_cart else {"product_id": "HP001", "name": "Sony WH-1000XM5 Wireless Headphones", "price": 24990.0}
            primary_prod = catalogue_engine.get_product(primary_item.get("product_id", "HP001"), db) or primary_item
            
            # Find the actual cross-sell mapped to this specific product
            cross_id = primary_prod.get("cross_sell_products", [None])[0] if isinstance(primary_prod, dict) and primary_prod.get("cross_sell_products") else "ACC001"
            cross_prod = catalogue_engine.get_product(cross_id, db) or catalogue_engine.get_product("ACC001", db) or {
                "product_id": "ACC001",
                "name": "Anker 65W GaN Fast Charger",
                "price": 2499.0
            }

            cart_items = [
                {"product_id": primary_prod["product_id"], "name": primary_prod["name"], "price": primary_prod["price"], "quantity": 1},
                {"product_id": cross_prod["product_id"], "name": cross_prod["name"], "price": cross_prod["price"], "quantity": 1}
            ]
            growth_calc = growth_engine.calculate_cart_growth([cart_items[0]], [cart_items[1]], bundle_discount_pct=5.0)

            audit_logger.log_step(
                session_id=session_id,
                stage="UPSELL_CROSS_SELL_ATTACHED",
                action_name="ATTACH_CROSS_SELL_BUNDLE",
                decision_explanation=f"Attached complementary '{cross_prod['name']}' to '{primary_prod['name']}'. Total expanded from ₹{growth_calc['baseline_amount']:,.2f} to ₹{growth_calc['final_total']:,.2f} (+{growth_calc['aov_lift_percentage']}% AOV lift).",
                policy_status="PASSED",
                money_amount=growth_calc["final_total"],
                metadata={"growth_calc": growth_calc},
                db=db
            )

            return {
                "session_id": session_id,
                "message": (
                    f"🎉 Great choice! I've added the **{cross_prod['name']}** (₹{cross_prod['price']:,.0f}) to your cart.\n\n"
                    f"💰 **Bundle Summary**:\n"
                    f"• {primary_prod['name']}: ₹{primary_prod['price']:,.0f}\n"
                    f"• {cross_prod['name']}: ₹{cross_prod['price']:,.0f}\n"
                    f"• 5% Instant Bundle Discount: -₹{growth_calc['discount_amount']:,.0f}\n"
                    f"**Total Amount**: **₹{growth_calc['final_total']:,.2f}** *(+₹{growth_calc['incremental_revenue']:,.2f} incremental value)*\n\n"
                    f"Ready to proceed? Say **'Checkout'** or click the checkout button."
                ),
                "intent": action_intent,
                "policy_status": "PASSED",
                "ready_for_checkout": False,
                "cart": {
                    "session_id": session_id,
                    "customer_id": customer_id,
                    "items": cart_items,
                    "base_total": growth_calc["baseline_amount"],
                    "discount_total": growth_calc["discount_amount"],
                    "final_total": growth_calc["final_total"],
                    "is_bundled": True,
                    "cross_sell_added": True,
                    "status": "CHECKOUT_PENDING"
                },
                "recommendations": []
            }

        # SCENARIO C: Add the first product / Add to cart
        elif action_intent == "ADD_FIRST":
            target_cat = parsed["category"] if parsed["category"] != "all" else None
            options = recommender_engine.recommend(intent_query=message, customer_id=customer_id, budget=parsed["budget"], category=target_cat, db=db)
            top_opt = options[0] if options else None
            if not top_opt:
                top_prod = catalogue_engine.get_product("HP001", db) or catalogue_engine.get_product("KB001", db)
            else:
                top_prod = top_opt["product"]

            new_cart = [{"product_id": top_prod["product_id"], "name": top_prod["name"], "price": top_prod["price"], "quantity": 1}]
            return {
                "session_id": session_id,
                "message": (
                    f"🛒 **Added to Cart**: **{top_prod['name']}** (₹{top_prod['price']:,.0f}).\n\n"
                    f"• In Stock: {top_prod.get('inventory', 25)} units\n"
                    f"• Delivery: {top_prod.get('delivery_days', 1)} day(s) express dispatch\n"
                    f"• Rating: {top_prod.get('rating', 4.8)}★\n\n"
                    f"Say **'Suggest something useful'** to see matching accessories or **'Checkout'** to pay."
                ),
                "intent": action_intent,
                "cart": {
                    "session_id": session_id,
                    "customer_id": customer_id,
                    "items": new_cart,
                    "base_total": top_prod["price"],
                    "discount_total": 0.0,
                    "final_total": top_prod["price"],
                    "is_bundled": False,
                    "status": "ACTIVE"
                },
                "policy_status": "PASSED",
                "ready_for_checkout": False,
                "recommendations": options
            }

        # SCENARIO D: Compare top items
        elif action_intent == "COMPARE":
            target_cat = parsed["category"] if parsed["category"] != "all" else None
            options = recommender_engine.recommend(intent_query=message, customer_id=customer_id, budget=parsed["budget"], category=target_cat, db=db)
            if len(options) >= 2:
                p1 = options[0]["product"]
                p2 = options[1]["product"]
                s1 = options[0]["recommendation_score"]
                s2 = options[1]["recommendation_score"]
                price_diff = abs(p1["price"] - p2["price"])
                cheaper_name = p1["name"] if p1["price"] < p2["price"] else p2["name"]
                
                resp_lines = [
                    f"⚖️ **Side-by-Side Comparison**:\n",
                    f"**1. {p1['name']}** (Score: **{s1}/100** ⭐ Top Pick)",
                    f"   • Price: ₹{p1['price']:,.0f} (Discount: {p1.get('discount', 0)}%)",
                    f"   • Rating: {p1.get('rating', 4.8)}★ ({p1.get('review_count', 1000):,} reviews)",
                    f"   • Delivery: {p1.get('delivery_days', 1)} day | Stock: {p1.get('inventory', 20)} units",
                    f"\n**2. {p2['name']}** (Score: **{s2}/100**)",
                    f"   • Price: ₹{p2['price']:,.0f} (Discount: {p2.get('discount', 0)}%)",
                    f"   • Rating: {p2.get('rating', 4.7)}★ ({p2.get('review_count', 800):,} reviews)",
                    f"   • Delivery: {p2.get('delivery_days', 1)} day | Stock: {p2.get('inventory', 20)} units",
                    f"\n💡 **AI Verdict**: **{p1['name']}** scores higher overall. If budget is key, **{cheaper_name}** saves ₹{price_diff:,.0f}."
                ]
                return {
                    "session_id": session_id,
                    "message": "\n".join(resp_lines),
                    "intent": "COMPARE",
                    "recommendations": options[:2],
                    "policy_status": "PASSED",
                    "ready_for_checkout": False
                }

        # SCENARIO E: Suggest useful accessory / bundle
        elif action_intent == "SUGGEST_USEFUL":
            primary_item = current_cart[0] if current_cart else None
            if primary_item:
                primary_prod = catalogue_engine.get_product(primary_item.get("product_id", "HP001"), db) or primary_item
            else:
                primary_prod = catalogue_engine.get_product("HP001", db) or catalogue_engine.get_product("KB001", db)

            bundle_data = growth_engine.generate_bundle(primary_prod.get("product_id", "HP001"), db)
            cs_name = bundle_data["cross_sell_product"]["name"]
            cs_price = bundle_data["cross_sell_product"]["price"]
            disc = bundle_data["bundle_discount_amount"]
            b_total = bundle_data["bundle_price"]

            return {
                "session_id": session_id,
                "message": (
                    f"🎁 **Recommended Add-On for {primary_prod['name']}**:\n\n"
                    f"• **{cs_name}** (₹{cs_price:,.0f})\n"
                    f"• **Bundle Benefit**: Instant 5% combo discount saves -₹{disc:,.0f}!\n"
                    f"• **Combo Total**: **₹{b_total:,.2f}**\n\n"
                    f"Say **'Add cross-sell'** to include it in your cart or **'Checkout'** for standalone."
                ),
                "intent": "SUGGEST_USEFUL",
                "bundle_offer": bundle_data,
                "cross_sell_offer": bundle_data["cross_sell_product"],
                "policy_status": "PASSED",
                "ready_for_checkout": False
            }

        # SCENARIO F: Natural Language & Voice Discovery (Multi-Category Search & Ranking)
        target_cat = parsed["category"] if parsed["category"] != "all" else None
        
        # Adjust budget / sort if cheaper or premium requested
        custom_budget = parsed["budget"]
        if action_intent == "CHEAPER" and current_cart:
            custom_budget = current_cart[0]["price"] * 0.85
        
        options = recommender_engine.recommend(
            intent_query=message,
            customer_id=customer_id,
            budget=custom_budget,
            category=target_cat,
            db=db
        )

        if action_intent == "CHEAPER" and options:
            options.sort(key=lambda x: x["product"]["price"])
            for rank, opt in enumerate(options[:4], 1):
                opt["rank"] = rank
                opt["is_top_pick"] = (rank == 1)
        elif action_intent == "PREMIUM" and options:
            options.sort(key=lambda x: x["product"]["price"], reverse=True)
            for rank, opt in enumerate(options[:4], 1):
                opt["rank"] = rank
                opt["is_top_pick"] = (rank == 1)

        top_opt = options[0] if options else None
        top_prod = top_opt["product"] if top_opt else None

        audit_logger.log_step(
            session_id=session_id,
            stage="PRODUCT_SEARCH_AND_RANKING",
            action_name="RANK_CATALOGUE_OPTIONS",
            decision_explanation=f"Ranked {len(options)} products for query '{message}' (Category: {parsed['category']}). Top pick '{top_prod['name'] if top_prod else 'None'}' (Score: {top_opt['recommendation_score'] if top_opt else 0}/100).",
            policy_status="PASSED",
            money_amount=top_prod["price"] if top_prod else None,
            metadata={"top_product": top_prod["product_id"] if top_prod else None, "score": top_opt["recommendation_score"] if top_prod else None},
            db=db
        )

        cross_sell = top_opt.get("cross_sell_opportunity") if top_opt else None
        category_name = parsed["category"].replace("_", " ").title() if parsed["category"] != "all" else "curated"
        lang_label = parsed.get("detected_language", "English (Global)")

        if "Hindi" in lang_label:
            resp_lines = [
                f"🌐 **[पहचानी गई भाषा: हिंदी / Hinglish]** आपके अनुरोध के अनुसार **{len(options)} {category_name} प्रोडक्ट्स** उपलब्ध हैं:"
            ]
        elif "Tamil" in lang_label:
            resp_lines = [
                f"🌐 **[கண்டறியப்பட்ட மொழி: தமிழ்]** உங்கள் கோரிக்கைக்கான **{len(options)} சிறந்த தயாரிப்புகள்** இதோ:"
            ]
        elif "Spanish" in lang_label:
            resp_lines = [
                f"🌐 **[Idioma detectado: Español]** He seleccionado **{len(options)} opciones** para ti:"
            ]
        else:
            resp_lines = [
                f"I analyzed our merchant catalogue and found **{len(options)} {category_name} options** matching your request:"
            ]

        for opt in options:
            badge = " ⭐ **TOP PICK**" if opt["is_top_pick"] else ""
            p = opt["product"]
            resp_lines.append(f"\n**Option {opt['rank']}: {p['name']} — ₹{p['price']:,.0f}**{badge} *(AI Score: {opt['recommendation_score']}/100)*")
            for b in opt["why_recommended"][:2]:
                resp_lines.append(f"  {b}")

        if top_prod:
            resp_lines.append(
                f"\n💡 **AI Score Rationale**: **Option {top_opt['rank']} ({top_prod['name']})** has {top_prod['rating']}★ customer rating, {top_prod.get('inventory', 25)} in stock, and {top_prod.get('delivery_days', 1)}-day express delivery."
            )

        if cross_sell:
            resp_lines.append(
                f"\n🛍️ **Cross-Sell Opportunity**: Would you like to add the matching **{cross_sell['name']} for ₹{cross_sell['price']:,.0f}**? *(Saves 5% when bundled)*"
            )

        return {
            "session_id": session_id,
            "message": "\n".join(resp_lines),
            "intent": action_intent,
            "detected_language": lang_label,
            "recommendations": options,
            "cross_sell_offer": cross_sell,
            "upsell_offer": top_opt.get("upsell_opportunity") if top_opt else None,
            "bundle_offer": growth_engine.generate_bundle(top_prod["product_id"], db) if top_prod else None,
            "cart": {
                "session_id": session_id,
                "customer_id": customer_id,
                "items": [{"product_id": top_prod["product_id"], "name": top_prod["name"], "price": top_prod["price"], "quantity": 1}] if top_prod else [],
                "base_total": top_prod["price"] if top_prod else 0.0,
                "discount_total": 0.0,
                "final_total": top_prod["price"] if top_prod else 0.0,
                "is_bundled": False,
                "status": "ACTIVE"
            } if top_prod else None,
            "policy_status": "PASSED",
            "ready_for_checkout": False
        }

agentic_checkout = AgenticCheckoutEngine()
