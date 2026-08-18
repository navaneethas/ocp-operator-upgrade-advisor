from typing import Dict, Any
from app.models import ClusterVersion

def parse_clusterversion(data: Dict[str, Any]) -> ClusterVersion:
    """
    Parse clusterversion JSON from 'oc get clusterversion version -o json'

    Args:
        data: Raw JSON dict from oc command

    Returns:
        ClusterVersion model
    """
    spec = data.get("spec", {})
    status = data.get("status", {})
    desired = status.get("desired", {})

    version = desired.get("version", "")
    channel = spec.get("channel", "")
    cluster_id = spec.get("clusterID", "")
    upstream = spec.get("upstream", "")

    return ClusterVersion(
        version=version,
        channel=channel,
        cluster_id=cluster_id,
        upstream=upstream
    )
