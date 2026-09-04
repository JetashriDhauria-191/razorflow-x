from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class NormalizedProduct:
    """
    Standard normalized product model across all connected providers.
    Honesty rule: Only sets original_price and discount if legitimately verified from provider.
    """
    def __init__(
        self,
        product_id: str,
        name: str,
        brand: str,
        category: str,
        price: float,
        currency: str = "INR",
        subcategory: Optional[str] = None,
        original_price: Optional[float] = None,
        discount: Optional[float] = None,
        rating: Optional[float] = 4.8,
        review_count: Optional[int] = 120,
        image_url: str = "",
        product_url: Optional[str] = None,
        source_name: str = "Storefront Demo Catalogue",
        source_type: str = "local_demo_catalogue",
        is_live: bool = False,
        is_buyable: bool = True,
        inventory: int = 25,
        delivery_days: int = 1,
        description: str = "",
        specifications: Optional[List[str]] = None,
        features: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        last_updated: Optional[str] = None,
        ai_score: int = 90,
        ai_reasons: Optional[List[str]] = None,
        badges: Optional[List[str]] = None
    ):
        self.product_id = str(product_id)
        self.id = str(product_id)
        self.name = name
        self.brand = brand or "Authentic"
        self.category = (category or "general").lower()
        self.subcategory = subcategory or self.category.title()
        self.sub_category = self.subcategory
        self.price = float(price)
        self.current_price = float(price)
        self.currency = currency
        
        if original_price is not None and float(original_price) > float(price):
            self.original_price = float(original_price)
            calc_disc = round(((float(original_price) - float(price)) / float(original_price)) * 100)
            self.discount = float(discount) if discount is not None else float(calc_disc)
        else:
            self.original_price = None
            self.discount = None

        self.rating = round(float(rating), 2) if rating is not None else 4.8
        self.review_count = int(review_count) if review_count is not None else 120
        self.image_url = image_url or "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
        self.product_url = product_url or f"/#product/{self.product_id}"
        self.source_url = self.product_url
        self.source_name = source_name
        self.source = source_name
        self.source_type = source_type
        self.is_live = bool(is_live)
        self.is_demo = not bool(is_live)
        self.is_buyable = bool(is_buyable)
        self.inventory = int(inventory)
        self.stock = int(inventory)
        self.delivery_days = int(delivery_days)
        self.delivery_sla = "1-Day Express" if self.delivery_days <= 1 else ("2-Day Standard" if self.delivery_days == 2 else f"{self.delivery_days}-Day Regional")
        self.description = description
        self.specifications = specifications or features or []
        self.features = self.specifications
        self.tags = tags or [self.category, self.brand.lower()]
        self.last_updated = last_updated or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.retrieved_at = self.last_updated
        self.ai_score = int(ai_score)
        self.ai_reasons = ai_reasons or []
        self.badges = badges or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.product_id,
            "product_id": self.product_id,
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "subcategory": self.subcategory,
            "sub_category": self.subcategory,
            "price": self.price,
            "current_price": self.price,
            "currency": self.currency,
            "original_price": self.original_price,
            "discount": self.discount,
            "rating": self.rating,
            "review_count": self.review_count,
            "image_url": self.image_url,
            "image": self.image_url,
            "product_url": self.product_url,
            "source_url": self.product_url,
            "source_name": self.source_name,
            "source": self.source_name,
            "source_type": self.source_type,
            "is_live": self.is_live,
            "is_demo": self.is_demo,
            "is_buyable": self.is_buyable,
            "inventory": self.inventory,
            "stock": self.inventory,
            "delivery_days": self.delivery_days,
            "delivery_sla": self.delivery_sla,
            "description": self.description,
            "specifications": self.specifications,
            "features": self.features,
            "tags": self.tags,
            "last_updated": self.last_updated,
            "retrieved_at": self.last_updated,
            "ai_score": self.ai_score,
            "ai_reasons": self.ai_reasons,
            "badges": self.badges
        }

class ProductProvider(ABC):
    name: str = "BaseProvider"
    provider_type: str = "base"
    is_live: bool = False

    @abstractmethod
    def search(self, query: str, intent: Dict[str, Any], context: Dict[str, Any]) -> List[NormalizedProduct]:
        pass

    @abstractmethod
    def get_product(self, product_id: str) -> Optional[NormalizedProduct]:
        pass

    @abstractmethod
    def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        pass
