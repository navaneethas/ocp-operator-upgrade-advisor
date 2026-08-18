#!/usr/bin/env python3
"""
OpenShift Operator Upgrade Advisor - Enhanced CLI
Uses real compatibility matrix from oc-mirror data
Works in supportshell environments
"""

import json
import sys
import re
import argparse
from datetime import datetime
from pathlib import Path

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def load_compatibility_matrix():
    """Load compatibility matrix from JSON file"""
    # Try multiple locations
    locations = [
        Path(__file__).parent / "compatibility_matrix.json",
        Path("compatibility_matrix.json"),
        Path("/Users/nsenthil/AI_TOOL/openshift-upgrade-advisor/compatibility_matrix.json")
    ]

    for location in locations:
        if location.exists():
            with open(location, 'r') as f:
                return json.load(f)

    print(f"{Colors.FAIL}Error: compatibility_matrix.json not found!{Colors.ENDC}")
    print("Please ensure compatibility_matrix.json is in the same directory as this script.")
    sys.exit(1)

# Load matrix at startup
COMPATIBILITY_MATRIX = load_compatibility_matrix()

def parse_clusterversion(data):
    """Parse cluster version from data"""
    spec = data.get("spec", {})
    status = data.get("status", {})
    desired = status.get("desired", {})
    return {
        "version": desired.get("version", ""),
        "channel": spec.get("channel", ""),
    }

def parse_subscriptions(data):
    """Parse subscriptions from data"""
    subscriptions = []
    items = data.get("items", []) if isinstance(data.get("items"), list) else []

    for item in items:
        if not isinstance(item, dict):
            continue
        metadata = item.get("metadata", {})
        spec = item.get("spec", {})
        status = item.get("status", {})

        subscriptions.append({
            "name": metadata.get("name", ""),
            "namespace": metadata.get("namespace", ""),
            "package": spec.get("name", ""),
            "channel": spec.get("channel", ""),
            "current_csv": status.get("currentCSV", ""),
            "install_plan_approval": spec.get("installPlanApproval", "Automatic"),
            "source": spec.get("source", ""),
            "source_namespace": spec.get("sourceNamespace", ""),
        })
    return subscriptions

def parse_csvs(data):
    """Parse CSVs from data"""
    csvs = []
    items = data.get("items", []) if isinstance(data.get("items"), list) else []

    for item in items:
        if not isinstance(item, dict):
            continue
        metadata = item.get("metadata", {})
        spec = item.get("spec", {})

        csvs.append({
            "name": metadata.get("name", ""),
            "namespace": metadata.get("namespace", ""),
            "version": spec.get("version", ""),
        })
    return csvs

def normalize_version(version):
    """
    Normalize version string by removing build metadata
    Examples:
      2.4.0+0.1785427615 -> 2.4.0
      1.10.6-rhel8 -> 1.10.6
      2.13.10 -> 2.13.10
    """
    if not version:
        return version

    # Remove build metadata after + or -
    # SemVer format: MAJOR.MINOR.PATCH[+BUILD][-PRERELEASE]
    version = re.split(r'[+\-]', version)[0]
    return version.strip()

def find_max_supported_ocp_version(operator_name, current_version):
    """Find the maximum OpenShift version that supports the current operator version"""
    if operator_name not in COMPATIBILITY_MATRIX:
        return None

    # Normalize the current version (remove build metadata)
    normalized_version = normalize_version(current_version)

    max_ocp_version = None
    operator_data = COMPATIBILITY_MATRIX[operator_name]

    # Check all OCP versions from newest to oldest
    for ocp_version in sorted(operator_data.keys(), reverse=True):
        supported_versions = operator_data[ocp_version]

        # Check if normalized version matches any supported version
        if normalized_version in supported_versions:
            max_ocp_version = ocp_version
            break

    return max_ocp_version

def version_matches(current_version, catalog_versions):
    """Check if current version exists in catalog versions"""
    # Normalize version before matching
    normalized_version = normalize_version(current_version)
    return normalized_version in catalog_versions

def check_compatibility(operator_name, current_version, target_ocp, catalog_source=None):
    """Check operator compatibility with enhanced max OCP info"""

    # Check if operator is from non-Red Hat catalog
    if catalog_source:
        non_redhat_catalogs = [
            'certified-operators',
            'community-operators',
            'redhat-marketplace',
            'custom-operators'
        ]

        for non_rh_catalog in non_redhat_catalogs:
            if non_rh_catalog in catalog_source.lower():
                catalog_type = catalog_source.replace('-', ' ').title()
                return {
                    "operator_name": operator_name,
                    "current_version": current_version,
                    "status": "not_redhat_operator",
                    "catalog_source": catalog_source,
                    "supported_versions": [],
                    "max_supported_ocp": None,
                    "explanation": f"Sorry, this operator is from {catalog_type}. The compatibility checker is currently designed for Red Hat operators only. Please check the operator's documentation for compatibility information."
                }

    # Check if operator exists in matrix
    if operator_name not in COMPATIBILITY_MATRIX:
        return {
            "operator_name": operator_name,
            "current_version": current_version,
            "status": "unknown",
            "supported_versions": [],
            "max_supported_ocp": None,
            "explanation": f"No compatibility data available for {operator_name}. This may be a community, certified, or custom operator. The compatibility checker is designed for Red Hat operators only."
        }

    # Get supported versions for target OCP
    supported_versions = COMPATIBILITY_MATRIX[operator_name].get(target_ocp, [])

    # Find max OCP version supporting current version
    max_ocp = find_max_supported_ocp_version(operator_name, current_version)

    # Check if current version is compatible with target OCP
    is_compatible = version_matches(current_version, supported_versions)

    if is_compatible:
        return {
            "operator_name": operator_name,
            "current_version": current_version,
            "status": "compatible",
            "supported_versions": supported_versions,
            "max_supported_ocp": max_ocp,
            "explanation": f"{operator_name} v{current_version} is compatible with OpenShift {target_ocp}. Current version supported up to OCP {max_ocp}."
        }
    else:
        if supported_versions:
            recommended_version = supported_versions[-1]  # Latest version

            return {
                "operator_name": operator_name,
                "current_version": current_version,
                "status": "incompatible_upgrade_required",
                "supported_versions": supported_versions,
                "max_supported_ocp": max_ocp,
                "recommended_version": recommended_version,
                "explanation": f"{operator_name} v{current_version} is only supported up to OCP {max_ocp}. Target OCP {target_ocp} requires upgrade to v{recommended_version}."
            }
        else:
            return {
                "operator_name": operator_name,
                "current_version": current_version,
                "status": "incompatible",
                "supported_versions": [],
                "max_supported_ocp": max_ocp,
                "explanation": f"{operator_name} v{current_version} not available in OpenShift {target_ocp} catalog."
            }

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n")

def print_summary(cluster_info, results):
    """Print analysis summary"""
    print(f"{Colors.BOLD}Cluster Information:{Colors.ENDC}")
    print(f"  Current Version:  {Colors.OKCYAN}{cluster_info['current_version']}{Colors.ENDC}")
    print(f"  Target Version:   {Colors.OKCYAN}{cluster_info['target_version']}{Colors.ENDC}")
    print(f"  Total Operators:  {cluster_info['total_operators']}")

    compatible = cluster_info['compatible_count']
    upgrade_req = cluster_info['upgrade_required_count']
    incompatible = cluster_info['unsupported_count']
    unknown = cluster_info.get('unknown_count', 0)

    print(f"\n{Colors.BOLD}Compatibility Summary:{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}✓ Compatible:{Colors.ENDC}          {compatible}")
    print(f"  {Colors.WARNING}⚠ Upgrade Required:{Colors.ENDC}    {upgrade_req}")
    print(f"  {Colors.FAIL}✗ Incompatible:{Colors.ENDC}        {incompatible}")
    if unknown > 0:
        print(f"  {Colors.OKBLUE}? Unknown:{Colors.ENDC}             {unknown}")

def print_operator_result(result, index):
    """Print individual operator result"""
    status = result['status']

    # Color based on status
    if status == 'compatible':
        status_color = Colors.OKGREEN
        status_icon = "✓"
    elif status in ['upgrade_required', 'incompatible_upgrade_required']:
        status_color = Colors.WARNING
        status_icon = "⚠"
    elif status == 'not_redhat_operator':
        status_color = Colors.OKCYAN
        status_icon = "ℹ"
    elif status == 'unknown':
        status_color = Colors.OKBLUE
        status_icon = "?"
    else:
        status_color = Colors.FAIL
        status_icon = "✗"

    print(f"\n{Colors.BOLD}[{index}] {result['operator_name']}{Colors.ENDC}")
    print(f"  Current Version:    {result['current_version']}")

    # Show catalog source if it's a non-Red Hat operator
    if result.get('catalog_source'):
        print(f"  Catalog Source:     {result['catalog_source']}")

    print(f"  Status:             {status_color}{status_icon} {status.replace('_', ' ').title()}{Colors.ENDC}")

    # Only show Max Supported OCP for Red Hat operators
    if status != 'not_redhat_operator':
        print(f"  Max Supported OCP:  {result.get('max_supported_ocp', 'N/A')}")

    if result.get('recommended_version'):
        print(f"  Recommended:        {Colors.OKGREEN}{result['recommended_version']}{Colors.ENDC}")

    # Show available versions in target OCP (always show, even if empty)
    target_ocp = result.get('target_ocp', 'Target')
    versions_list = result.get('supported_versions', [])

    if versions_list:
        if len(versions_list) <= 5:
            versions = ', '.join(versions_list)
        else:
            versions = ', '.join(versions_list[:5]) + f" ... ({len(versions_list)} total)"
        print(f"  Available in {target_ocp}: {versions}")
    else:
        # Show even when no versions available (incompatible)
        print(f"  Available in {target_ocp}: {Colors.FAIL}(not in catalog){Colors.ENDC}")

    print(f"  {Colors.BOLD}Explanation:{Colors.ENDC} {result['explanation']}")

def analyze_data_file(data_file, target_ocp):
    """Analyze data file and display results"""
    try:
        # Load JSON data
        with open(data_file, 'r') as f:
            data = json.load(f)

        # Parse cluster data
        cluster_data = data.get('cluster_data', {})
        cluster_version = parse_clusterversion(cluster_data.get("clusterVersion", {}))
        subscriptions = parse_subscriptions(cluster_data.get("subscriptions", {}))
        csvs = parse_csvs(cluster_data.get("clusterServiceVersions", {}))

        # Map CSVs by name
        csv_map = {csv["name"]: csv for csv in csvs}

        # Analyze each subscription
        results = []
        for sub in subscriptions:
            csv_name = sub["current_csv"]
            if csv_name and csv_name in csv_map:
                csv = csv_map[csv_name]
                # Pass catalog source for non-Red Hat operator detection
                catalog_source = sub.get("source", "")
                result = check_compatibility(sub["package"], csv["version"], target_ocp, catalog_source)
                result["channel"] = sub.get("channel", "N/A")
                result["catalog_source"] = catalog_source
                result["target_ocp"] = target_ocp  # Add target OCP for display
                results.append(result)

        # Calculate summary
        compatible_count = sum(1 for r in results if r["status"] == "compatible")
        upgrade_count = sum(1 for r in results if r["status"] in ["upgrade_required", "incompatible_upgrade_required"])
        incompatible_count = sum(1 for r in results if r["status"] == "incompatible")
        unknown_count = sum(1 for r in results if r["status"] == "unknown")

        cluster_info = {
            "current_version": cluster_version["version"],
            "target_version": target_ocp,
            "total_operators": len(results),
            "compatible_count": compatible_count,
            "upgrade_required_count": upgrade_count,
            "unsupported_count": incompatible_count,
            "unknown_count": unknown_count,
        }

        # Display results
        print_header("OpenShift Operator Upgrade Advisor - Analysis Report")
        print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Compatibility Matrix: {len(COMPATIBILITY_MATRIX)} operators loaded")
        print()

        print_summary(cluster_info, results)

        print(f"\n{Colors.BOLD}{Colors.HEADER}{'─' * 80}{Colors.ENDC}")
        print(f"{Colors.BOLD}Detailed Operator Analysis{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'─' * 80}{Colors.ENDC}")

        for idx, result in enumerate(results, 1):
            print_operator_result(result, idx)

        print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n")

        return 0

    except FileNotFoundError:
        print(f"{Colors.FAIL}Error: File '{data_file}' not found{Colors.ENDC}")
        return 1
    except Exception as e:
        print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    parser = argparse.ArgumentParser(
        description='OpenShift Operator Upgrade Advisor - Enhanced CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze operators for OpenShift 4.21
  %(prog)s openshift-data.json --target-ocp 4.21

  # Analyze with interactive target version selection
  %(prog)s openshift-data.json
        """
    )

    parser.add_argument('data_file', help='Path to JSON file containing cluster data')
    parser.add_argument('--target-ocp', '-t',
                        help='Target OpenShift version (e.g., 4.21)',
                        default=None)

    args = parser.parse_args()

    # Get target OCP version
    target_ocp = args.target_ocp
    if not target_ocp:
        print(f"{Colors.BOLD}Enter target OpenShift version (e.g., 4.21): {Colors.ENDC}", end='')
        target_ocp = input().strip()
        if not target_ocp:
            print(f"{Colors.FAIL}Error: Target OCP version is required{Colors.ENDC}")
            return 1

    return analyze_data_file(args.data_file, target_ocp)

if __name__ == '__main__':
    sys.exit(main())
