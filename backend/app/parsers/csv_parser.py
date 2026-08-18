from typing import Dict, Any, List
from app.models import CSV

def parse_csvs(data: Dict[str, Any]) -> List[CSV]:
    """
    Parse CSVs (ClusterServiceVersions) JSON from 'oc get csv -A -o json'

    Args:
        data: Raw JSON dict from oc command

    Returns:
        List of CSV models
    """
    csvs = []
    items = data.get("items", [])

    for item in items:
        metadata = item.get("metadata", {})
        spec = item.get("spec", {})
        annotations = metadata.get("annotations", {})

        name = metadata.get("name", "")
        version = spec.get("version", "")

        replaces = spec.get("replaces")
        skips = spec.get("skips", [])
        skip_range = annotations.get("olm.skipRange")

        csv = CSV(
            name=name,
            namespace=metadata.get("namespace", ""),
            version=version,
            display_name=spec.get("displayName"),
            description=spec.get("description"),
            replaces=replaces,
            skips=skips if isinstance(skips, list) else [],
            skip_range=skip_range
        )
        csvs.append(csv)

    return csvs
