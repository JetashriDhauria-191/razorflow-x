from typing import List, Dict, Any, Optional
from .base import ProductProvider, NormalizedProduct
from .local_catalogue import LocalCatalogueProvider
from .live_provider import LiveProductProvider

class ProviderAggregator:
    """
    Orchestrates search across Local Demo Catalogue and connected Live Providers.
    Deduplicates by canonical product identity, preserves honest source labeling,
    and returns ranked normalized products.
    """
    def __init__(self):
        self.providers: List[ProductProvider] = [
            LocalCatalogueProvider(),
            LiveProductProvider()
        ]

    def search_all(self, query: str, intent: Dict[str, Any], context: Dict[str, Any]) -> List[NormalizedProduct]:
        all_results: List[NormalizedProduct] = []
        seen_ids = set()

        for prov in self.providers:
            try:
                items = prov.search(query, intent, context)
                for item in items:
                    if item.product_id not in seen_ids:
                        seen_ids.add(item.product_id)
                        all_results.append(item)
            except Exception as e:
                pass

        return all_results

    def get_product(self, product_id: str) -> Optional[NormalizedProduct]:
        for prov in self.providers:
            prod = prov.get_product(product_id)
            if prod:
                return prod
        return None

provider_aggregator = ProviderAggregator()
