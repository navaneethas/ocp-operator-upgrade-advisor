# OpenShift Operator Compatibility Checker

## Description
Check if operators are compatible with target OpenShift version before upgrade. Analyzes operator versions and recommends upgrades if needed.

## Usage
Use this skill when:
- Planning an OpenShift cluster upgrade
- Checking operator compatibility with a specific OCP version
- Need to know which operators require upgrades
- Want to see recommended operator versions for target OCP

## Prerequisites
- Access to OpenShift cluster (must-gather or direct oc access)
- Python 3.6 or higher available in supportshell

## Data Collection

### From Live Cluster (if oc access available)
```bash
(echo '{"clusterVersion":'; oc get clusterversion version -o json; \
 echo ',"subscriptions":'; oc get sub -A -o json; \
 echo ',"clusterServiceVersions":'; oc get csv -A -o json; \
 echo '}') > cluster-data.json
```

### From Must-Gather (typical supportshell scenario)
```bash
# Extract required data from must-gather
cd must-gather-directory

# Get clusterversion
(echo '{"clusterVersion":'; cat */cluster-scoped-resources/config.openshift.io/clusterversions/version.yaml | python3 -c "import yaml, json, sys; print(json.dumps(yaml.safe_load(sys.stdin)))"; \
 echo ',"subscriptions":'; cat */namespaces/*/operators.coreos.com/subscriptions/*.yaml | python3 -c "import yaml, json, sys; docs=list(yaml.safe_load_all(sys.stdin)); print(json.dumps({'items': docs}))"; \
 echo ',"clusterServiceVersions":'; cat */namespaces/*/operators.coreos.com/clusterserviceversions/*.yaml | python3 -c "import yaml, json, sys; docs=list(yaml.safe_load_all(sys.stdin)); print(json.dumps({'items': docs}))"; \
 echo '}') > cluster-data.json
```

## Analysis Script

### CLI Analyzer (Copy-Paste into supportshell)

Save this as `check-operator-compatibility.py`:

```python
#!/usr/bin/env python3
"""
OpenShift Operator Compatibility Checker
Standalone version for supportshell - no external dependencies
"""

import json
import sys
import re
from datetime import datetime

# ANSI colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Compatibility matrix - embedded for offline use
COMPATIBILITY_MATRIX_URL = "https://raw.githubusercontent.com/yourusername/openshift-upgrade-advisor/main/compatibility_matrix.json"

def normalize_version(version):
    """Remove build metadata from version string"""
    if not version:
        return version
    version = re.split(r'[+\-]', version)[0]
    return version.strip()

def parse_clusterversion(data):
    """Parse cluster version"""
    spec = data.get("spec", {})
    status = data.get("status", {})
    desired = status.get("desired", {})
    return {
        "version": desired.get("version", ""),
        "channel": spec.get("channel", ""),
    }

def parse_subscriptions(data):
    """Parse subscriptions"""
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
            "source": spec.get("source", ""),
        })
    return subscriptions

def parse_csvs(data):
    """Parse CSVs"""
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

def check_compatibility(operator_name, current_version, target_ocp, matrix, catalog_source=None):
    """Check operator compatibility"""
    
    # Check if non-Red Hat operator
    if catalog_source:
        non_redhat = ['certified-operators', 'community-operators', 'redhat-marketplace']
        for nrh in non_redhat:
            if nrh in catalog_source.lower():
                return {
                    "operator_name": operator_name,
                    "current_version": current_version,
                    "status": "not_redhat_operator",
                    "explanation": f"This operator is from {catalog_source}. Only Red Hat operators are checked.",
                }
    
    if operator_name not in matrix:
        return {
            "operator_name": operator_name,
            "current_version": current_version,
            "status": "unknown",
            "explanation": f"No compatibility data for {operator_name}. May be community/certified operator.",
        }
    
    normalized_version = normalize_version(current_version)
    supported_versions = matrix[operator_name].get(target_ocp, [])
    
    # Find max OCP
    max_ocp = None
    for ocp in sorted(matrix[operator_name].keys(), reverse=True):
        if normalized_version in matrix[operator_name][ocp]:
            max_ocp = ocp
            break
    
    is_compatible = normalized_version in supported_versions
    
    if is_compatible:
        return {
            "operator_name": operator_name,
            "current_version": current_version,
            "status": "compatible",
            "max_supported_ocp": max_ocp,
            "supported_versions": supported_versions,
            "explanation": f"{operator_name} v{current_version} is compatible with OCP {target_ocp}."
        }
    else:
        if supported_versions:
            recommended = supported_versions[-1]
            return {
                "operator_name": operator_name,
                "current_version": current_version,
                "status": "upgrade_required",
                "max_supported_ocp": max_ocp,
                "recommended_version": recommended,
                "supported_versions": supported_versions,
                "explanation": f"{operator_name} v{current_version} only supported up to OCP {max_ocp}. Upgrade to v{recommended} for OCP {target_ocp}."
            }
        else:
            return {
                "operator_name": operator_name,
                "current_version": current_version,
                "status": "incompatible",
                "max_supported_ocp": max_ocp,
                "explanation": f"{operator_name} v{current_version} not available in OCP {target_ocp} catalog."
            }

def analyze(data_file, target_ocp, matrix_file=None):
    """Main analysis function"""
    
    # Load compatibility matrix
    if matrix_file:
        with open(matrix_file) as f:
            matrix = json.load(f)
    else:
        print(f"{Colors.WARNING}Warning: No compatibility matrix provided. Download from:{Colors.ENDC}")
        print(f"{COMPATIBILITY_MATRIX_URL}")
        return 1
    
    # Load cluster data
    with open(data_file) as f:
        data = json.load(f)
    
    cluster_data = data.get('cluster_data', data)
    cluster_version = parse_clusterversion(cluster_data.get("clusterVersion", {}))
    subscriptions = parse_subscriptions(cluster_data.get("subscriptions", {}))
    csvs = parse_csvs(cluster_data.get("clusterServiceVersions", {}))
    
    csv_map = {csv["name"]: csv for csv in csvs}
    
    # Analyze
    results = []
    for sub in subscriptions:
        csv_name = sub["current_csv"]
        if csv_name and csv_name in csv_map:
            csv = csv_map[csv_name]
            result = check_compatibility(sub["package"], csv["version"], target_ocp, matrix, sub.get("source"))
            result["channel"] = sub.get("channel", "N/A")
            results.append(result)
    
    # Display results
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'OpenShift Operator Compatibility Report':^80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Cluster Information:{Colors.ENDC}")
    print(f"  Current OCP:  {Colors.OKCYAN}{cluster_version['version']}{Colors.ENDC}")
    print(f"  Target OCP:   {Colors.OKCYAN}{target_ocp}{Colors.ENDC}")
    print(f"  Total Operators: {len(results)}")
    
    compatible = sum(1 for r in results if r.get("status") == "compatible")
    upgrade_req = sum(1 for r in results if r.get("status") == "upgrade_required")
    incompatible = sum(1 for r in results if r.get("status") == "incompatible")
    
    print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}✓ Compatible:{Colors.ENDC} {compatible}")
    print(f"  {Colors.WARNING}⚠ Upgrade Required:{Colors.ENDC} {upgrade_req}")
    print(f"  {Colors.FAIL}✗ Incompatible:{Colors.ENDC} {incompatible}")
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'─'*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}Detailed Analysis{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'─'*80}{Colors.ENDC}")
    
    for idx, result in enumerate(results, 1):
        status = result.get("status", "unknown")
        
        if status == "compatible":
            icon = f"{Colors.OKGREEN}✓{Colors.ENDC}"
        elif status == "upgrade_required":
            icon = f"{Colors.WARNING}⚠{Colors.ENDC}"
        elif status == "not_redhat_operator":
            icon = f"{Colors.OKCYAN}ℹ{Colors.ENDC}"
        else:
            icon = f"{Colors.FAIL}✗{Colors.ENDC}"
        
        print(f"\n{Colors.BOLD}[{idx}] {result['operator_name']}{Colors.ENDC}")
        print(f"  Current Version: {result['current_version']}")
        print(f"  Status: {icon} {status.replace('_', ' ').title()}")
        
        if result.get("max_supported_ocp"):
            print(f"  Max OCP: {result['max_supported_ocp']}")
        
        if result.get("recommended_version"):
            print(f"  {Colors.OKGREEN}Recommended: {result['recommended_version']}{Colors.ENDC}")
        
        if result.get("supported_versions"):
            versions = result["supported_versions"]
            if len(versions) <= 5:
                print(f"  Available in {target_ocp}: {', '.join(versions)}")
            else:
                print(f"  Available in {target_ocp}: {', '.join(versions[:5])} ... ({len(versions)} total)")
        
        print(f"  {Colors.BOLD}→{Colors.ENDC} {result['explanation']}")
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 check-operator-compatibility.py <cluster-data.json> <target-ocp> [compatibility-matrix.json]")
        print("\nExample: python3 check-operator-compatibility.py cluster-data.json 4.22 compatibility_matrix.json")
        sys.exit(1)
    
    data_file = sys.argv[1]
    target_ocp = sys.argv[2]
    matrix_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    sys.exit(analyze(data_file, target_ocp, matrix_file))
```

## Quick Usage in Supportshell

### Step 1: Download compatibility matrix
```bash
curl -o compatibility_matrix.json https://raw.githubusercontent.com/yourusername/openshift-upgrade-advisor/main/compatibility_matrix.json
```

### Step 2: Download analyzer script
```bash
curl -o check-operator-compatibility.py https://raw.githubusercontent.com/yourusername/openshift-upgrade-advisor/main/cli-analyzer-enhanced.py
```

### Step 3: Collect data from must-gather
```bash
cd /path/to/must-gather

# Simple collection (if YAML files available)
(echo '{"clusterVersion":'; cat */cluster-scoped-resources/config.openshift.io/clusterversions/version.yaml | python3 -c "import yaml, json, sys; print(json.dumps(yaml.safe_load(sys.stdin)))"; \
 echo ',"subscriptions":'; find . -path "*/operators.coreos.com/subscriptions/*.yaml" -exec cat {} \; | python3 -c "import yaml, json, sys; docs=[d for d in yaml.safe_load_all(sys.stdin) if d]; print(json.dumps({'items': docs}))"; \
 echo ',"clusterServiceVersions":'; find . -path "*/operators.coreos.com/clusterserviceversions/*.yaml" -exec cat {} \; | python3 -c "import yaml, json, sys; docs=[d for d in yaml.safe_load_all(sys.stdin) if d]; print(json.dumps({'items': docs}))"; \
 echo '}') > cluster-data.json
```

### Step 4: Run analysis
```bash
python3 check-operator-compatibility.py cluster-data.json 4.22 compatibility_matrix.json
```

## Expected Output

```
================================================================================
          OpenShift Operator Compatibility Report          
================================================================================

Cluster Information:
  Current OCP:  4.20.15
  Target OCP:   4.22
  Total Operators: 8

Summary:
  ✓ Compatible: 5
  ⚠ Upgrade Required: 2
  ✗ Incompatible: 1

────────────────────────────────────────────────────────────────────────────────
Detailed Analysis
────────────────────────────────────────────────────────────────────────────────

[1] openshift-gitops-operator
  Current Version: 1.10.6
  Status: ✓ Compatible
  Max OCP: 4.22
  Available in 4.22: 1.6.6, 1.7.4, 1.8.6, 1.9.4, 1.10.6 ... (16 total)
  → openshift-gitops-operator v1.10.6 is compatible with OCP 4.22.

[2] advanced-cluster-management
  Current Version: 2.9.9
  Status: ⚠ Upgrade Required
  Max OCP: 4.15
  Recommended: 2.17.0
  Available in 4.22: 2.16.2, 2.17.0
  → advanced-cluster-management v2.9.9 only supported up to OCP 4.15. 
    Upgrade to v2.17.0 for OCP 4.22.
```

## Troubleshooting

### Issue: PyYAML not available
**Solution**: Use JSON format instead or install PyYAML in supportshell if allowed

### Issue: Cannot find operator data in must-gather
**Solution**: Check must-gather was collected properly:
```bash
find . -name "subscriptions" -type d
find . -name "clusterserviceversions" -type d
```

### Issue: Matrix file too large to download
**Solution**: The matrix is ~103KB, should work in most supportshells. If needed, contact for alternative.

## Notes

- Works offline once matrix is downloaded
- No external dependencies except Python 3 standard library
- Handles version metadata (e.g., `2.4.0+0.12345`)
- Detects non-Red Hat operators automatically
- Coverage: 180 Red Hat operators, OCP 4.12-4.22

## Author
Created for supportshell environments where full tool installation isn't possible.

## Version
1.0.0 - Compatible with must-gather and live clusters
