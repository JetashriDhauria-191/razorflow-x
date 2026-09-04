import os
import json
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
try:
    from backend.models import Product
except (ImportError, ModuleNotFoundError):
    from models import Product

DATA_JSON = os.path.join(os.path.dirname(__file__), "catalogue_data.json")

def _load_products():
    if os.path.exists(DATA_JSON):
        try:
            with open(DATA_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

SEED_PRODUCTS = _load_products()

def get_image_for_query(query: str, category: str = None) -> str:
    q = (query + " " + (category or "")).lower()
    if any(w in q for w in ["headphone", "headset", "audio", "mic", "hedfone"]):
        return "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600"
    elif any(w in q for w in ["earbud", "earbuds", "tws", "airpod"]):
        return "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600"
    elif any(w in q for w in ["shoe", "shoes", "sneaker", "joota", "juta", "running", "chappal", "seruppu", "cheppulu"]):
        return "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600"
    elif any(w in q for w in ["laptop", "macbook", "notebook", "ultrabook", "coding"]):
        return "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600"
    elif any(w in q for w in ["phone", "smartphone", "iphone", "galaxy", "pixel", "mobile"]):
        return "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600"
    elif any(w in q for w in ["watch", "smartwatch", "fitness", "band", "ghadi"]):
        return "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600"
    elif any(w in q for w in ["keyboard", "keys", "mechanical", "keycaps"]):
        return "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600"
    elif any(w in q for w in ["mouse", "mice", "pointer", "trackball"]):
        return "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600"
    elif any(w in q for w in ["monitor", "display", "screen", "4k"]):
        return "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600"
    elif any(w in q for w in ["camera", "dslr", "mirrorless", "gimbal"]):
        return "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600"
    elif any(w in q for w in ["bag", "backpack", "sling", "luggage"]):
        return "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600"
    elif any(w in q for w in ["shirt", "tshirt", "dress", "jeans", "clothing"]):
        return "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600"
    elif any(w in q for w in ["book", "books", "coding book", "programming"]):
        return "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600"
    elif any(w in q for w in ["cooker", "fryer", "mixer", "grinder", "kitchen"]):
        return "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600"
    elif any(w in q for w in ["ac", "air conditioner", "fridge", "refrigerator", "washing machine", "vacuum"]):
        return "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=600"
    elif any(w in q for w in ["beauty", "trimmer", "grooming", "dryer", "perfume"]):
        return "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600"
    elif any(w in q for w in ["sports", "yoga", "gym", "fitness", "cricket"]):
        return "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600"
    elif any(w in q for w in ["gaming", "playstation", "ps5", "xbox"]):
        return "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=600"
    return "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600"

class CatalogueEngine:
    def __init__(self):
        self._memory_cache = {}
        self._category_index = {}
        self._reload_cache()

    def _reload_cache(self):
        global SEED_PRODUCTS
        SEED_PRODUCTS = _load_products()
        self._memory_cache = {p["product_id"]: p for p in SEED_PRODUCTS}
        self._category_index = {}
        for p in SEED_PRODUCTS:
            c = p.get("category", "general").lower()
            if c not in self._category_index:
                self._category_index[c] = []
            self._category_index[c].append(p)

    def seed_db(self, db: Session) -> None:
        try:
            count = db.query(Product).count()
            if count < 100:
                new_records = []
                for p in SEED_PRODUCTS:
                    new_records.append(Product(
                        id=p["product_id"],
                        name=p["name"],
                        category=p["category"],
                        brand=p.get("brand", "Authentic Store"),
                        price=p["price"],
                        original_price=p.get("reference_price", p.get("original_price", p["price"] * 1.2)),
                        discount=p.get("discount", 15.0),
                        inventory=p.get("inventory", 25),
                        stock=p.get("inventory", 25),
                        in_stock=True,
                        delivery_days=p.get("delivery_days", 1),
                        delivery_sla=p.get("delivery_sla", "1-Day Express"),
                        rating=p.get("rating", 4.8),
                        review_count=p.get("review_count", 120),
                        image_url=p.get("image_url", "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=500"),
                        source=p.get("price_source", "Storefront Demo Catalogue"),
                        description=p.get("description", "Verified Storefront Product SKU"),
                        specifications=p.get("specifications", []),
                        tags=p.get("tags", []),
                        cross_sell_products=p.get("cross_sell_products", []),
                        upsell_products=p.get("upsell_products", [])
                    ))
                if new_records:
                    db.bulk_save_objects(new_records)
                    db.commit()
        except Exception:
            pass

    def get_all_products(self, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        return list(self._memory_cache.values())

    def get_product(self, product_id: str, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        return self._memory_cache.get(product_id)

    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        in_stock_only: bool = False,
        tag: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        db: Optional[Session] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        # Fast category filtering
        if category and category.lower() != "all":
            c_low = category.lower()
            pool = self._category_index.get(c_low, [])
            if not pool:
                for cat_key, items in self._category_index.items():
                    if c_low in cat_key or cat_key in c_low:
                        pool = items
                        break
        else:
            pool = list(self._memory_cache.values())

        # Price ceiling filter
        if max_price is not None and max_price > 0:
            pool = [p for p in pool if p["price"] <= max_price]

        # Rating filter
        if min_rating is not None and min_rating > 0:
            pool = [p for p in pool if p.get("rating", 4.0) >= min_rating]

        # Inventory filter
        if in_stock_only:
            pool = [p for p in pool if p.get("inventory", p.get("stock", 0)) > 0]

        # Semantic & Keyword scoring
        if query:
            q_clean = query.lower().strip()
            tokens = [t for t in re.split(r'\s+', q_clean) if len(t) > 1]
            matched = []
            unmatched = []
            for p in pool:
                p_text = f"{p['name']} {p['category']} {p.get('subcategory', '')} {p.get('brand', '')} {' '.join(p.get('tags', []))} {' '.join(p.get('aliases', []))} {p.get('description', '')}".lower()
                matches = sum(1 for t in tokens if t in p_text)
                if matches > 0:
                    matched.append((matches, p))
                else:
                    unmatched.append(p)
            matched.sort(key=lambda x: x[0], reverse=True)
            matched_items = [item[1] for item in matched]
            
            if category and category.lower() != "all":
                results = matched_items + unmatched
            elif matched_items:
                results = matched_items
            else:
                results = pool
        else:
            results = pool

        return results[offset:offset + limit]

catalogue_engine = CatalogueEngine()
