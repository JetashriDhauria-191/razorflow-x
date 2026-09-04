import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import ProductProvider, NormalizedProduct

try:
    from backend.catalogue import catalogue_engine
except ImportError:
    from catalogue import catalogue_engine

class LocalCatalogueProvider(ProductProvider):
    name = "Storefront Demo Catalogue"
    provider_type = "local_demo_catalogue"
    is_live = False

    def search(self, query: str, intent: Dict[str, Any], context: Dict[str, Any]) -> List[NormalizedProduct]:
        cat_filter = intent.get("category")
        budget = intent.get("budget")
        brand = intent.get("brand")
        limit = intent.get("limit", 50)
        offset = intent.get("offset", 0)

        search_q = query
        if intent.get("is_follow_up") and cat_filter:
            search_q = cat_filter
        elif cat_filter and not any(k in query.lower() for k in ["a", "b", "c", "d", "e"]):
            search_q = cat_filter

        raw_items = catalogue_engine.search(
            query=search_q,
            category=cat_filter,
            max_price=budget,
            in_stock_only=False,
            limit=limit,
            offset=offset
        )

        results: List[NormalizedProduct] = []
        for raw in raw_items:
            if brand and brand.lower() not in (raw.get("brand", "") + " " + raw.get("name", "")).lower():
                continue

            del_days = int(raw.get("delivery_days", 1))
            if raw.get("category") in ["appliances", "kitchen", "decor", "furniture"]:
                del_days = max(2, del_days)

            norm = NormalizedProduct(
                product_id=raw.get("product_id") or raw.get("id"),
                name=raw.get("name", "Store Product"),
                brand=raw.get("brand", "Authentic Store"),
                category=raw.get("category", "general"),
                subcategory=raw.get("sub_category") or raw.get("subcategory"),
                price=float(raw.get("price", 0)),
                currency="INR",
                original_price=raw.get("original_price"),
                discount=raw.get("discount"),
                rating=float(raw.get("rating", 4.8)),
                review_count=int(raw.get("review_count", 120)),
                image_url=raw.get("image_url") or raw.get("image"),
                product_url=f"/#product/{raw.get('product_id') or raw.get('id')}",
                source_name="Storefront Demo Catalogue",
                source_type="local_demo_catalogue",
                is_live=False,
                is_buyable=True,
                inventory=int(raw.get("inventory", raw.get("stock", 25))),
                delivery_days=del_days,
                description=raw.get("description", "Verified local demo SKU"),
                specifications=raw.get("specifications") or raw.get("features") or [],
                tags=raw.get("tags") or [],
                last_updated=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            )
            results.append(norm)

        return results

    def get_product(self, product_id: str) -> Optional[NormalizedProduct]:
        raw = catalogue_engine.get_product(product_id)
        if not raw:
            return None
        return NormalizedProduct(
            product_id=raw.get("product_id") or raw.get("id"),
            name=raw.get("name", "Store Product"),
            brand=raw.get("brand", "Authentic Store"),
            category=raw.get("category", "general"),
            subcategory=raw.get("sub_category") or raw.get("subcategory"),
            price=float(raw.get("price", 0)),
            currency="INR",
            original_price=raw.get("original_price"),
            discount=raw.get("discount"),
            rating=float(raw.get("rating", 4.8)),
            review_count=int(raw.get("review_count", 120)),
            image_url=raw.get("image_url") or raw.get("image"),
            product_url=f"/#product/{raw.get('product_id') or raw.get('id')}",
            source_name="Storefront Demo Catalogue",
            source_type="local_demo_catalogue",
            is_live=False,
            is_buyable=True,
            inventory=int(raw.get("inventory", raw.get("stock", 25))),
            delivery_days=int(raw.get("delivery_days", 1)),
            description=raw.get("description", ""),
            specifications=raw.get("specifications") or raw.get("features") or [],
            tags=raw.get("tags") or []
        )

    def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        p = self.get_product(product_id)
        return p.to_dict() if p else None
