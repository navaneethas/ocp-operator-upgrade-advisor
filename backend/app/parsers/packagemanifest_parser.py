from typing import Dict, Any, List
from app.models import PackageManifest, PackageChannel

def parse_packagemanifests(data: Dict[str, Any]) -> List[PackageManifest]:
    """
    Parse packagemanifests JSON from 'oc get packagemanifest -o json'

    Args:
        data: Raw JSON dict from oc command

    Returns:
        List of PackageManifest models
    """
    packagemanifests = []
    items = data.get("items", [])

    for item in items:
        metadata = item.get("metadata", {})
        status = item.get("status", {})

        package_name = metadata.get("name", "")
        catalog_source = status.get("catalogSource", "")
        catalog_source_namespace = status.get("catalogSourceNamespace", "")
        default_channel = status.get("defaultChannel")

        channels = []
        for channel_data in status.get("channels", []):
            channel = PackageChannel(
                name=channel_data.get("name", ""),
                current_csv=channel_data.get("currentCSV", ""),
                current_csv_version=channel_data.get("currentCSVDesc", {}).get("version")
            )
            channels.append(channel)

        manifest = PackageManifest(
            package_name=package_name,
            catalog_source=catalog_source,
            catalog_source_namespace=catalog_source_namespace,
            default_channel=default_channel,
            channels=channels
        )
        packagemanifests.append(manifest)

    return packagemanifests
