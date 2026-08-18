#!/usr/bin/env python3
"""
OpenShift Operator Upgrade Advisor - Universal CLI
Handles BOTH JSON and YAML formats
Uses ONLY Python standard library (no external dependencies)
Works in supportshell environments without installations
"""

import json
import sys
import argparse
import re
from datetime import datetime

# Compatibility Matrix - Updated for OpenShift 4.12 through 4.22
COMPATIBILITY_MATRIX = {
    "gitops-operator": {
        "4.12": ["1.8", "1.9", "1.10"],
        "4.13": ["1.9", "1.10", "1.11", "1.12"],
        "4.14": ["1.10", "1.11", "1.12", "1.13"],
        "4.15": ["1.11", "1.12", "1.13", "1.14"],
        "4.16": ["1.13", "1.14", "1.15"],
        "4.17": ["1.14", "1.15", "1.16"],
        "4.18": ["1.15", "1.16", "1.17"],
        "4.19": ["1.16", "1.17", "1.18"],
        "4.20": ["1.17", "1.18", "1.19", "1.20"],
        "4.21": ["1.18", "1.19", "1.20", "1.21"],
        "4.22": ["1.19", "1.20", "1.21", "1.22"],
    },
    "openshift-gitops-operator": {
        "4.12": ["1.8", "1.9", "1.10"],
        "4.13": ["1.9", "1.10", "1.11", "1.12"],
        "4.14": ["1.10", "1.11", "1.12", "1.13"],
        "4.15": ["1.11", "1.12", "1.13", "1.14"],
        "4.16": ["1.13", "1.14", "1.15"],
        "4.17": ["1.14", "1.15", "1.16"],
        "4.18": ["1.15", "1.16", "1.17"],
        "4.19": ["1.16", "1.17", "1.18"],
        "4.20": ["1.17", "1.18", "1.19", "1.20"],
        "4.21": ["1.18", "1.19", "1.20", "1.21"],
        "4.22": ["1.19", "1.20", "1.21", "1.22"],
    },
    "quay-operator": {
        "4.12": ["3.8", "3.9"],
        "4.13": ["3.9", "3.10"],
        "4.14": ["3.10", "3.11"],
        "4.15": ["3.11", "3.12"],
        "4.16": ["3.12", "3.13"],
        "4.17": ["3.13", "3.14"],
        "4.18": ["3.14", "3.15"],
        "4.19": ["3.15", "3.16"],
        "4.20": ["3.16", "3.17"],
        "4.21": ["3.17", "3.18"],
        "4.22": ["3.18", "3.19"],
    },
    "cluster-logging": {
        "4.12": ["5.6", "5.7"],
        "4.13": ["5.7", "5.8"],
        "4.14": ["5.8", "5.9"],
        "4.15": ["5.9", "6.0"],
        "4.16": ["6.0", "6.1"],
        "4.17": ["6.1", "6.2"],
        "4.18": ["6.2", "6.3"],
        "4.19": ["6.3", "6.4"],
        "4.20": ["6.4", "6.5"],
        "4.21": ["6.5", "6.6"],
        "4.22": ["6.6", "6.7"],
    },
    "openshift-pipelines-operator-rh": {
        "4.12": ["1.12", "1.13"],
        "4.13": ["1.13", "1.14"],
        "4.14": ["1.14", "1.15"],
        "4.15": ["1.15", "1.16"],
        "4.16": ["1.16", "1.17"],
        "4.17": ["1.17", "1.18"],
        "4.18": ["1.18", "1.19"],
        "4.19": ["1.19", "1.20"],
        "4.20": ["1.20", "1.21"],
        "4.21": ["1.21", "1.22"],
        "4.22": ["1.22", "1.23"],
    },
    "advanced-cluster-management": {
        "4.12": ["2.7", "2.8"],
        "4.13": ["2.8", "2.9"],
        "4.14": ["2.9", "2.10"],
        "4.15": ["2.10", "2.11"],
        "4.16": ["2.11", "2.12"],
        "4.17": ["2.12", "2.13"],
        "4.18": ["2.13", "2.14"],
        "4.19": ["2.13", "2.14", "2.15"],
        "4.20": ["2.14", "2.15", "2.16"],
        "4.21": ["2.15", "2.16", "2.17"],
        "4.22": ["2.16", "2.17", "2.18"],
    },
    "servicemeshoperator3": {
        "4.12": ["3.0", "3.1"],
        "4.13": ["3.0", "3.1"],
        "4.14": ["3.1", "3.2"],
        "4.15": ["3.1", "3.2"],
        "4.16": ["3.1", "3.2"],
        "4.17": ["3.1", "3.2"],
        "4.18": ["3.2", "3.3"],
        "4.19": ["3.2", "3.3"],
        "4.20": ["3.3", "3.4"],
        "4.21": ["3.3", "3.4", "3.5"],
        "4.22": ["3.4", "3.5"],
    },
}

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def simple_yaml_to_dict(yaml_text):
    """
    Simple YAML parser for oc command output
    Only handles the specific structure we need - NOT a full YAML parser
    Uses only Python stdlib
    """
    def parse_value(value):
        """Parse YAML value to Python type"""
        value = value.strip()
        if value == 'null' or value == '':
            return None
        if value == 'true':
            return True
        if value == 'false':
            return False
        if value.isdigit():
            return int(value)
        # Try to parse as float
        try:
            return float(value)
        except ValueError:
            pass
        # Remove quotes
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        return value

    def parse_yaml_block(lines, indent=0):
        """Recursively parse YAML block"""
        result = {}
        current_list = []
        current_key = None
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                i += 1
                continue

            # Calculate indentation
            line_indent = len(line) - len(line.lstrip())

            # If less indented, we're done with this block
            if line_indent < indent:
                break

            # Skip if not at our indent level
            if line_indent > indent:
                i += 1
                continue

            stripped = line.strip()

            # List item
            if stripped.startswith('- '):
                item_content = stripped[2:].strip()
                if ':' in item_content:
                    # Dict item in list
                    key, val = item_content.split(':', 1)
                    item_dict = {key.strip(): parse_value(val.strip())}

                    # Look ahead for nested items
                    j = i + 1
                    nested_lines = []
                    while j < len(lines):
                        next_line = lines[j]
                        next_indent = len(next_line) - len(next_line.lstrip())
                        if next_indent > line_indent:
                            nested_lines.append(next_line)
                            j += 1
                        else:
                            break

                    if nested_lines:
                        nested = parse_yaml_block(nested_lines, line_indent + 2)
                        item_dict.update(nested)
                        i = j - 1

                    current_list.append(item_dict)
                else:
                    current_list.append(parse_value(item_content))

            # Key-value pair
            elif ':' in stripped:
                key, val = stripped.split(':', 1)
                key = key.strip()
                val = val.strip()

                if val:
                    # Inline value
                    result[key] = parse_value(val)
                else:
                    # Look ahead for nested content
                    j = i + 1
                    nested_lines = []
                    while j < len(lines):
                        next_line = lines[j]
                        next_indent = len(next_line) - len(next_line.lstrip())
                        if next_indent > line_indent:
                            nested_lines.append(next_line)
                            j += 1
                        else:
                            break

                    if nested_lines:
                        # Check if it's a list or dict
                        if nested_lines[0].strip().startswith('- '):
                            temp_result = parse_yaml_block(nested_lines, line_indent + 2)
                            if 'items' in temp_result or any(nested_lines[0].strip().startswith('- ') for l in nested_lines):
                                # It's a list
                                current_list = []
                                for line in nested_lines:
                                    if line.strip().startswith('- '):
                                        item_lines = [line]
                                        # Gather all lines for this item
                                        idx = nested_lines.index(line) + 1
                                        base_indent = len(line) - len(line.lstrip())
                                        while idx < len(nested_lines):
                                            next_item_indent = len(nested_lines[idx]) - len(nested_lines[idx].lstrip())
                                            if nested_lines[idx].strip().startswith('- '):
                                                break
                                            if next_item_indent > base_indent:
                                                item_lines.append(nested_lines[idx])
                                                idx += 1
                                            else:
                                                break

                                        item_data = parse_yaml_block(item_lines, base_indent)
                                        current_list.append(item_data)

                                result[key] = current_list if current_list else []
                                current_list = []
                        else:
                            result[key] = parse_yaml_block(nested_lines, line_indent + 2)
                        i = j - 1
                    else:
                        result[key] = None

            i += 1

        # If we collected list items but no key, return as list
        if current_list and not result:
            return current_list

        return result

    lines = yaml_text.split('\n')
    return parse_yaml_block(lines)

def load_data_file(file_path):
    """Load data file - automatically detects JSON or YAML format"""
    with open(file_path, 'r') as f:
        content = f.read()

    # Try JSON first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try simple YAML parsing
        try:
            return simple_yaml_to_dict(content)
        except Exception as e:
            raise ValueError(f"Could not parse file as JSON or YAML: {e}")

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

def find_max_supported_ocp_version(operator_name, current_version):
    """Find the maximum OpenShift version that supports the current operator version"""
    base_name = operator_name.split('.')[0] if '.' in operator_name else operator_name

    if base_name not in COMPATIBILITY_MATRIX:
        return None

    max_ocp_version = None
    operator_data = COMPATIBILITY_MATRIX[base_name]

    for ocp_version in sorted(operator_data.keys(), reverse=True):
        supported_versions = operator_data[ocp_version]
        if any(current_version.startswith(v) for v in supported_versions):
            max_ocp_version = ocp_version
            break

    return max_ocp_version

def check_compatibility(operator_name, current_version, target_ocp):
    """Check operator compatibility"""
    base_name = operator_name.split('.')[0] if '.' in operator_name else operator_name

    supported_versions = []
    if base_name in COMPATIBILITY_MATRIX:
        supported_versions = COMPATIBILITY_MATRIX[base_name].get(target_ocp, [])

    max_ocp = find_max_supported_ocp_version(operator_name, current_version)
    is_compatible = any(current_version.startswith(v) for v in supported_versions)

    if is_compatible:
        return {
            "operator_name": operator_name,
            "current_version": current_version,
            "status": "compatible",
            "supported_versions": supported_versions,
            "max_supported_ocp": max_ocp,
            "explanation": f"{operator_name} version {current_version} is compatible with OpenShift {target_ocp}.",
            "risk_level": "low"
        }
    else:
        if supported_versions:
            recommended_version = supported_versions[-1]

            if max_ocp and max_ocp < target_ocp:
                return {
                    "operator_name": operator_name,
                    "current_version": current_version,
                    "status": "incompatible_upgrade_required",
                    "supported_versions": supported_versions,
                    "max_supported_ocp": max_ocp,
                    "recommended_version": recommended_version,
                    "explanation": f"{operator_name} version {current_version} is incompatible. Please upgrade to {recommended_version}.",
                    "risk_level": "high"
                }
            else:
                return {
                    "operator_name": operator_name,
                    "current_version": current_version,
                    "status": "upgrade_required",
                    "target_version": recommended_version,
                    "supported_versions": supported_versions,
                    "max_supported_ocp": max_ocp,
                    "explanation": f"{operator_name} requires upgrade to {recommended_version}.",
                    "risk_level": "medium"
                }
        else:
            return {
                "operator_name": operator_name,
                "current_version": current_version,
                "status": "incompatible",
                "supported_versions": [],
                "max_supported_ocp": max_ocp,
                "explanation": f"{operator_name} is incompatible with OpenShift {target_ocp}.",
                "risk_level": "critical"
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

    print(f"\n{Colors.BOLD}Compatibility Summary:{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}✓ Compatible:{Colors.ENDC}          {compatible}")
    print(f"  {Colors.WARNING}⚠ Upgrade Required:{Colors.ENDC}    {upgrade_req}")
    print(f"  {Colors.FAIL}✗ Incompatible:{Colors.ENDC}        {incompatible}")

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
    else:
        status_color = Colors.FAIL
        status_icon = "✗"

    print(f"\n{Colors.BOLD}[{index}] {result['operator_name']}{Colors.ENDC}")
    print(f"  Current Version:    {result['current_version']}")
    print(f"  Status:             {status_color}{status_icon} {status.replace('_', ' ').title()}{Colors.ENDC}")
    print(f"  Max Supported OCP:  {result.get('max_supported_ocp', 'N/A')}")

    if result.get('recommended_version'):
        print(f"  Recommended:        {Colors.OKGREEN}{result['recommended_version']}{Colors.ENDC}")

    if result.get('supported_versions'):
        versions = ', '.join(result['supported_versions'])
        print(f"  Supported Versions: {versions}")

    print(f"  Risk Level:         {result['risk_level'].upper()}")
    print(f"  {Colors.BOLD}Explanation:{Colors.ENDC} {result['explanation']}")

def print_risk_assessment(risk_score, summary):
    """Print overall risk assessment"""
    print(f"\n{Colors.BOLD}Risk Assessment:{Colors.ENDC}")

    if risk_score == 'critical':
        color = Colors.FAIL
        icon = "🔴"
    elif risk_score == 'high':
        color = Colors.FAIL
        icon = "🟠"
    elif risk_score == 'medium':
        color = Colors.WARNING
        icon = "🟡"
    else:
        color = Colors.OKGREEN
        icon = "🟢"

    print(f"  {color}{icon} {risk_score.upper()}: {summary}{Colors.ENDC}")

def analyze_data_file(data_file, target_ocp):
    """Analyze data file and display results"""
    try:
        # Load data file (auto-detects JSON or YAML)
        data = load_data_file(data_file)

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
                result = check_compatibility(sub["package"], csv["version"], target_ocp)
                result["channel"] = sub.get("channel", "N/A")
                results.append(result)

        # Calculate summary
        compatible_count = sum(1 for r in results if r["status"] == "compatible")
        upgrade_count = sum(1 for r in results if r["status"] in ["upgrade_required", "incompatible_upgrade_required"])
        incompatible_count = sum(1 for r in results if r["status"] in ["incompatible", "incompatible_upgrade_required"])

        # Generate summary
        if incompatible_count > 0:
            risk = "critical"
            summary = f"{incompatible_count} incompatible operators found."
        elif upgrade_count > 2:
            risk = "high"
            summary = f"{upgrade_count} operators require upgrades."
        elif upgrade_count > 0:
            risk = "medium"
            summary = f"{upgrade_count} operators need upgrades."
        else:
            risk = "low"
            summary = "All operators are compatible."

        cluster_info = {
            "current_version": cluster_version["version"],
            "target_version": target_ocp,
            "total_operators": len(results),
            "compatible_count": compatible_count,
            "upgrade_required_count": upgrade_count,
            "unsupported_count": incompatible_count,
        }

        # Display results
        print_header("OpenShift Operator Upgrade Advisor - Analysis Report")
        print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print_summary(cluster_info, results)
        print_risk_assessment(risk, summary)

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
        description='OpenShift Operator Upgrade Advisor - Universal CLI (JSON & YAML Support, No Dependencies)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze operators for OpenShift 4.21
  %(prog)s openshift-data.json --target-ocp 4.21
  %(prog)s openshift-data.yaml --target-ocp 4.21

  # Analyze with interactive target version selection
  %(prog)s openshift-data.json
        """
    )

    parser.add_argument('data_file', help='Path to JSON or YAML file containing cluster data')
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
