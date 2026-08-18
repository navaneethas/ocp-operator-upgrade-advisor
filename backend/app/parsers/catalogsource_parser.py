from typing import Dict, Any, List
from app.models import CatalogSource

def parse_catalogsources(data: Dict[str, Any]) -> List[CatalogSource]:
    """
    Parse catalogsources JSON from 'oc get catalogsource -A -o json'

    Args:
        data: Raw JSON dict from oc command

    Returns:
        List of CatalogSource models
    """
    catalogsources = []
    items = data.get("items", [])

    for item in items:
        metadata = item.get("metadata", {})
        spec = item.get("spec", {})

        catalogsource = CatalogSource(
            name=metadata.get("name", ""),
            namespace=metadata.get("namespace", ""),
            display_name=spec.get("displayName"),
            publisher=spec.get("publisher"),
            source_type=spec.get("sourceType", ""),
            image=spec.get("image")
        )
        catalogsources.append(catalogsource)

    return catalogsources
