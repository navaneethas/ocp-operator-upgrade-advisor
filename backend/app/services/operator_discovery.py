from typing import List, Dict
from app.models import (
    Subscription,
    CSV,
    CatalogSource,
    PackageManifest,
    OperatorInfo
)

def discover_operators(
    subscriptions: List[Subscription],
    csvs: List[CSV],
    catalogsources: List[CatalogSource],
    packagemanifests: List[PackageManifest]
) -> List[OperatorInfo]:
    """
    Combine data from all sources to build complete operator information.

    Args:
        subscriptions: List of subscriptions
        csvs: List of CSVs
        catalogsources: List of catalog sources
        packagemanifests: List of package manifests

    Returns:
        List of OperatorInfo objects
    """
    operators = []

    csv_by_name = {csv.name: csv for csv in csvs}
    packagemanifest_by_name = {pm.package_name: pm for pm in packagemanifests}

    for subscription in subscriptions:
        csv_name = subscription.installed_csv or subscription.current_csv

        if not csv_name:
            continue

        csv = csv_by_name.get(csv_name)

        if not csv:
            continue

        package_manifest = packagemanifest_by_name.get(subscription.package)

        operator = OperatorInfo(
            name=subscription.package,
            namespace=subscription.namespace,
            current_csv=csv.name,
            current_version=csv.version,
            channel=subscription.channel,
            catalog_source=subscription.source,
            subscription=subscription,
            package_manifest=package_manifest
        )

        operators.append(operator)

    return operators
