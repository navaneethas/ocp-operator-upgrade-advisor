from typing import Dict, Any, List
from app.models import Subscription

def parse_subscriptions(data: Dict[str, Any]) -> List[Subscription]:
    """
    Parse subscriptions JSON from 'oc get sub -A -o json'

    Args:
        data: Raw JSON dict from oc command

    Returns:
        List of Subscription models
    """
    subscriptions = []
    items = data.get("items", [])

    for item in items:
        metadata = item.get("metadata", {})
        spec = item.get("spec", {})
        status = item.get("status", {})

        subscription = Subscription(
            name=metadata.get("name", ""),
            namespace=metadata.get("namespace", ""),
            package=spec.get("name", ""),
            channel=spec.get("channel", ""),
            source=spec.get("source", ""),
            source_namespace=spec.get("sourceNamespace", ""),
            current_csv=status.get("currentCSV"),
            installed_csv=status.get("installedCSV")
        )
        subscriptions.append(subscription)

    return subscriptions
