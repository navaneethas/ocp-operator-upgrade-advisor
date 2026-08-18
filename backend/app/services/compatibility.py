from typing import List, Dict, Optional
from app.models import (
    OperatorInfo,
    CompatibilityResult,
    CompatibilityStatus,
    RiskLevel,
    CSV
)
from app.services.graph import (
    build_upgrade_graph,
    find_upgrade_path,
    build_upgrade_path_model
)

COMPATIBILITY_MATRIX = {
    "gitops-operator": {
        "4.12": ["1.8", "1.9", "1.10"],
        "4.13": ["1.9", "1.10", "1.11", "1.12"],
        "4.14": ["1.10", "1.11", "1.12", "1.13"],
        "4.15": ["1.11", "1.12", "1.13", "1.14"],
        "4.16": ["1.13", "1.14", "1.15"],
        "4.17": ["1.14", "1.15", "1.16"],
    },
    "quay-operator": {
        "4.12": ["3.8", "3.9"],
        "4.13": ["3.9", "3.10"],
        "4.14": ["3.10", "3.11"],
        "4.15": ["3.11", "3.12"],
        "4.16": ["3.12", "3.13"],
        "4.17": ["3.13", "3.14"],
    },
    "cluster-logging": {
        "4.12": ["5.6", "5.7"],
        "4.13": ["5.7", "5.8"],
        "4.14": ["5.8", "5.9"],
        "4.15": ["5.9", "6.0"],
        "4.16": ["6.0", "6.1"],
        "4.17": ["6.1", "6.2"],
    },
    "openshift-pipelines-operator-rh": {
        "4.12": ["1.12", "1.13"],
        "4.13": ["1.13", "1.14"],
        "4.14": ["1.14", "1.15"],
        "4.15": ["1.15", "1.16"],
        "4.16": ["1.16", "1.17"],
        "4.17": ["1.17", "1.18"],
    }
}

def extract_operator_base_name(csv_name: str) -> str:
    """
    Extract base operator name from CSV name.

    Args:
        csv_name: Full CSV name (e.g., "gitops-operator.v1.12.0")

    Returns:
        Base operator name
    """
    if '.' in csv_name:
        return csv_name.split('.')[0]
    return csv_name

def check_operator_compatibility(
    operator: OperatorInfo,
    target_ocp_version: str,
    all_csvs: List[CSV]
) -> CompatibilityResult:
    """
    Check if operator is compatible with target OpenShift version.

    Args:
        operator: Operator information
        target_ocp_version: Target OpenShift version (e.g., "4.16")
        all_csvs: All CSVs for building upgrade graph

    Returns:
        CompatibilityResult with status and recommendations
    """
    base_name = extract_operator_base_name(operator.current_csv)
    current_version = operator.current_version

    supported_versions = find_supported_versions(base_name, target_ocp_version)

    is_compatible = is_version_supported(current_version, supported_versions)

    if is_compatible:
        return CompatibilityResult(
            operator_name=operator.name,
            current_version=current_version,
            status=CompatibilityStatus.COMPATIBLE,
            target_version=current_version,
            supported_versions=supported_versions,
            risk_level=RiskLevel.LOW
        )

    if supported_versions:
        target_version = supported_versions[-1]

        operator_csvs = [csv for csv in all_csvs if base_name in csv.name]
        graph = build_upgrade_graph(operator_csvs)
        path = find_upgrade_path(graph, current_version, target_version)

        if path:
            upgrade_path = build_upgrade_path_model(
                operator.name,
                current_version,
                target_version,
                path
            )
            return CompatibilityResult(
                operator_name=operator.name,
                current_version=current_version,
                status=CompatibilityStatus.UPGRADE_REQUIRED,
                target_version=target_version,
                supported_versions=supported_versions,
                upgrade_path=upgrade_path,
                risk_level=RiskLevel.MEDIUM
            )
        else:
            return CompatibilityResult(
                operator_name=operator.name,
                current_version=current_version,
                status=CompatibilityStatus.MANUAL_INTERVENTION,
                target_version=target_version,
                supported_versions=supported_versions,
                risk_level=RiskLevel.HIGH
            )

    return CompatibilityResult(
        operator_name=operator.name,
        current_version=current_version,
        status=CompatibilityStatus.UNSUPPORTED,
        supported_versions=[],
        risk_level=RiskLevel.CRITICAL
    )

def find_supported_versions(operator_base_name: str, target_ocp_version: str) -> List[str]:
    """
    Find supported operator versions for target OpenShift version.

    Args:
        operator_base_name: Base name of operator
        target_ocp_version: Target OpenShift version

    Returns:
        List of supported versions
    """
    if operator_base_name in COMPATIBILITY_MATRIX:
        operator_data = COMPATIBILITY_MATRIX[operator_base_name]
        return operator_data.get(target_ocp_version, [])

    return []

def is_version_supported(version: str, supported_versions: List[str]) -> bool:
    """
    Check if version is in supported versions list.

    Args:
        version: Version to check
        supported_versions: List of supported versions

    Returns:
        True if supported
    """
    version_normalized = version.lstrip('v')

    for supported in supported_versions:
        if version_normalized.startswith(supported):
            return True

    return False

def calculate_risk_level(
    compatibility_results: List[CompatibilityResult]
) -> RiskLevel:
    """
    Calculate overall risk level based on all compatibility results.

    Args:
        compatibility_results: List of compatibility results

    Returns:
        Overall risk level
    """
    risk_counts = {
        RiskLevel.LOW: 0,
        RiskLevel.MEDIUM: 0,
        RiskLevel.HIGH: 0,
        RiskLevel.CRITICAL: 0
    }

    for result in compatibility_results:
        risk_counts[result.risk_level] += 1

    if risk_counts[RiskLevel.CRITICAL] > 0:
        return RiskLevel.CRITICAL
    if risk_counts[RiskLevel.HIGH] > 0:
        return RiskLevel.HIGH
    if risk_counts[RiskLevel.MEDIUM] > 2:
        return RiskLevel.HIGH
    if risk_counts[RiskLevel.MEDIUM] > 0:
        return RiskLevel.MEDIUM

    return RiskLevel.LOW
