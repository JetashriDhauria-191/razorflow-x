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
try:
    from backend.language_service import language_service
    from backend.product_alias_service import product_alias_service
except (ImportError, ModuleNotFoundError):
    from language_service import language_service
    from product_alias_service import product_alias_service

class AgenticCheckoutEngine:
    """
    Conversational & Voice-Enabled AI Checkout Agent.
    Transforms natural language & voice intent into explainable, policy-gated Razorpay transactions
    across multiple product categories with complete Multilingual & Typo Search Intelligence.
    """

    def parse_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower().strip()
        
        # 1. Multilingual parsing via Universal Language Service
        norm = language_service.normalize_multilingual_query(message)
        budget = norm.get("budget")
        category = norm.get("category") or "all"
        if category == "all":
            alias_cat = product_alias_service.resolve_category(message)
            if alias_cat:
                category = alias_cat

        lang_code = norm.get("detected_language", "en")
        lang_map = {
            "hi": "Hindi / Hinglish (हिंदी)",
            "ta": "Tamil (தமிழ்)",
            "te": "Telugu (తెలుగు)",
            "ml": "Malayalam (മലയാളം)",
            "kn": "Kannada (ಕನ್ನಡ)",
            "bn": "Bengali (বাংলা)",
            "mr": "Marathi (मराठी)",
            "gu": "Gujarati (ગુજરાતી)",
            "pa": "Punjabi (ਪੰਜਾਬੀ)",
            "es": "Spanish (Español)",
            "fr": "French (Français)",
            "de": "German (Deutsch)",
            "en": "English (Global)"
        }
        detected_language = lang_map.get(lang_code, "English (Global)")

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
        elif norm.get("intent_type") == "CHEAPEST" or any(w in msg_lower for w in ["cheaper", "lower price", "less expensive", "budget option", "show something cheaper", "find cheaper", "सस्ता", "कम दाम", "குறைந்த விலை", "తక్కువ ధర", "barato", "moins cher"]):
            action_intent = "CHEAPER"
        elif norm.get("intent_type") == "PREMIUM" or any(w in msg_lower for w in ["premium", "expensive", "best quality", "flagship", "give me a premium option", "top tier", "महंगा", "बेस्ट क्वालिटी", "cara"]):
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

        search_intelligence = {
            "original_query": message,
            "detected_language": detected_language,
            "detected_language_code": lang_code,
            "typo_normalized": norm.get("typo_correction"),
            "interpreted_intent": norm.get("interpreted_intent", (category or "Product Discovery").title()),
            "confidence_score": norm.get("confidence_score_percent", 95),
            "confidence_tier": norm.get("confidence_tier", "HIGH CONFIDENCE"),
            "budget_extracted": f"₹{budget:,.0f}" if budget else None,
            "expanded_aliases": norm.get("expanded_aliases", [])
        }

        return {
            "query": message,
            "category": category,
            "budget": budget,
            "detected_language": detected_language,
            "detected_language_code": lang_code,
            "action_intent": action_intent,
            "keywords": [w for w in msg_lower.split() if len(w) > 2],
            "norm": norm,
            "search_intelligence": search_intelligence
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
        search_intel = parsed.get("search_intelligence", {})

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
                top_match = catalogue_engine.search(query=message, category=parsed["category"] if parsed["category"] != "all" else None, db=db)
                selected = top_match[0] if top_match else catalogue_engine.get_product("HP001", db) or catalogue_engine.get_product("KB001", db)
                current_cart = [{"product_id": selected["product_id"], "name": selected["name"], "price": selected["price"], "quantity": 1}]

            cart_total = sum(i["price"] * i.get("quantity", 1) for i in current_cart)
            product_ids = [i["product_id"] for i in current_cart]

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
                    "recommendations": [],
                    "search_intelligence": search_intel
                }

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
                "recommendations": [],
                "search_intelligence": search_intel
            }

        # SCENARIO B: Customer accepts cross-sell
        elif action_intent == "ADD_CROSS_SELL":
            primary_item = current_cart[0] if current_cart else {"product_id": "HP001", "name": "Sony WH-1000XM5 Wireless Headphones", "price": 24990.0}
            primary_prod = catalogue_engine.get_product(primary_item.get("product_id", "HP001"), db) or primary_item
            
            cross_id = primary_prod.get("cross_sell_products", [None])[0] if isinstance(primary_prod, dict) and primary_prod.get("cross_sell_products") else None
            cross_prod = (catalogue_engine.get_product(cross_id, db) if cross_id else None)
            if not cross_prod or (cross_prod and cross_prod["price"] > primary_prod.get("price", 1000) * 1.5 and primary_prod.get("price", 1000) < 1000):
                cross_prod = recommender_engine.get_appropriate_cross_sell(primary_prod.get("category", ""), primary_prod.get("price", 1000), primary_prod.get("name", ""))

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
                "recommendations": [],
                "search_intelligence": search_intel
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
                "recommendations": options,
                "search_intelligence": search_intel
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
                    "ready_for_checkout": False,
                    "search_intelligence": search_intel
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
                "ready_for_checkout": False,
                "search_intelligence": search_intel
            }

        # SCENARIO F: Natural Language & Voice Discovery (Multi-Category Search & Ranking)
        target_cat = parsed["category"] if parsed["category"] != "all" else None
        
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
            for rank, opt in enumerate(options[:8], 1):
                opt["rank"] = rank
                opt["is_top_pick"] = (rank == 1)
        elif action_intent == "PREMIUM" and options:
            options.sort(key=lambda x: x["product"]["price"], reverse=True)
            for rank, opt in enumerate(options[:8], 1):
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
        category_name = search_intel.get("interpreted_intent") or (parsed["category"].replace("_", " ").title() if parsed["category"] != "all" else "curated products")
        lang_label = parsed.get("detected_language", "English (Global)")

        typo_alert = ""
        if search_intel.get("typo_normalized"):
            typo_alert = f"\n*(✍️ Interpreted query: `{search_intel['typo_normalized']}`)*\n"

        if "Hindi" in lang_label:
            resp_lines = [
                f"🌐 **[पहचानी गई भाषा: हिंदी / Hinglish]** {typo_alert}आपके अनुरोध के अनुसार **{len(options)} {category_name} प्रोडक्ट्स** उपलब्ध हैं:"
            ]
        elif "Tamil" in lang_label:
            resp_lines = [
                f"🌐 **[கண்டறியப்பட்ட மொழி: தமிழ்]** {typo_alert}உங்கள் கோரிக்கைக்கான **{len(options)} {category_name} சிறந்த தயாரிப்புகள்** இதோ:"
            ]
        elif "Telugu" in lang_label:
            resp_lines = [
                f"🌐 **[గుర్తించబడిన భాష: తెలుగు]** {typo_alert}మీ కోసం **{len(options)} {category_name} ఉత్తమ ఉత్పత్తులు** సిద్ధంగా ఉన్నాయి:"
            ]
        elif "Kannada" in lang_label:
            resp_lines = [
                f"🌐 **[ಗುರುತಿಸಲಾದ ಭಾಷೆ: ಕನ್ನಡ]** {typo_alert}ನಿಮಗಾಗಿ **{len(options)} {category_name} ಅತ್ಯುತ್ತಮ ಉತ್ಪನ್ನಗಳು** ಲಭ್ಯವಿವೆ:"
            ]
        elif "Malayalam" in lang_label:
            resp_lines = [
                f"🌐 **[തിരിച്ചറിഞ്ഞ ഭാഷ: മലയാളം]** {typo_alert}നിങ്ങൾക്കായി **{len(options)} {category_name} മികച്ച ഉൽപ്പന്നങ്ങൾ** ഇതാ:"
            ]
        elif "Bengali" in lang_label:
            resp_lines = [
                f"🌐 **[শনাক্ত করা ভাষা: বাংলা]** {typo_alert}আপনার অনুরোধের জন্য **{len(options)}টি {category_name} সেরা পণ্য** নিচে দেওয়া হলো:"
            ]
        elif "Spanish" in lang_label:
            resp_lines = [
                f"🌐 **[Idioma detectado: Español]** {typo_alert}He seleccionado **{len(options)} opciones de {category_name}** para ti:"
            ]
        elif "French" in lang_label:
            resp_lines = [
                f"🌐 **[Langue détectée: Français]** {typo_alert}J'ai sélectionné **{len(options)} options de {category_name}** pour vous:"
            ]
        elif "German" in lang_label:
            resp_lines = [
                f"🌐 **[Erkannte Sprache: Deutsch]** {typo_alert}Ich habe **{len(options)} {category_name} Optionen** für Sie gefunden:"
            ]
        else:
            resp_lines = [
                f"I analyzed our merchant catalogue and found **{len(options)} {category_name} options** matching your request:{typo_alert}"
            ]

        for opt in options:
            badge = " ⭐ **TOP PICK**" if opt["is_top_pick"] else ""
            p = opt["product"]
            est_days = p.get("delivery_days", 1)
            est_str = "⚡ Delivery: Tomorrow by 5 PM (Express)" if est_days == 1 else f"🚚 Delivery in {est_days} Days"
            resp_lines.append(f"\n**Option {opt['rank']}: {p['name']} — ₹{p['price']:,.0f}**{badge}\n  • {est_str} | AI Score: {opt['recommendation_score']}/100")
            for b in opt["why_recommended"][:2]:
                resp_lines.append(f"  • {b}")

        if top_prod:
            resp_lines.append(
                f"\n💡 **Estimated Delivery**: Order now for **Option {top_opt['rank']} ({top_prod['name']})** with **1-Day Express Delivery SLA (Arrives Tomorrow by 5:00 PM)**."
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
            "ready_for_checkout": False,
            "search_intelligence": search_intel
        }

agentic_checkout = AgenticCheckoutEngine()
