#!/usr/bin/env python3
"""
Simplified OpenShift Operator Upgrade Advisor Server
Runs without pydantic - uses standard Python dict/dataclass
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime
import uuid

# Try to import YAML support (optional)
try:
    import yaml
    YAML_SUPPORT = True
except ImportError:
    YAML_SUPPORT = False

# Simple in-memory storage
analysis_cache = {}

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
    "openshift-gitops-operator": {  # Alternative name for gitops
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

def parse_clusterversion(data):
    """Parse cluster version from JSON"""
    spec = data.get("spec", {})
    status = data.get("status", {})
    desired = status.get("desired", {})
    return {
        "version": desired.get("version", ""),
        "channel": spec.get("channel", ""),
    }

def parse_subscriptions(data):
    """Parse subscriptions from JSON"""
    subscriptions = []
    for item in data.get("items", []):
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
    """Parse CSVs from JSON"""
    csvs = []
    for item in data.get("items", []):
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

    # Check all OCP versions to find the highest one that supports this operator version
    for ocp_version in sorted(operator_data.keys(), reverse=True):
        supported_versions = operator_data[ocp_version]
        if any(current_version.startswith(v) for v in supported_versions):
            max_ocp_version = ocp_version
            break

    return max_ocp_version

def version_to_tuple(version_str):
    """Convert version string to tuple for comparison (e.g., '1.21.1' -> (1, 21, 1))"""
    try:
        return tuple(map(int, version_str.split('.')))
    except:
        return (0, 0, 0)

def find_ocp_version_for_operator(operator_name, target_version):
    """Find which OpenShift version supports the target operator version"""
    base_name = operator_name.split('.')[0] if '.' in operator_name else operator_name

    if base_name not in COMPATIBILITY_MATRIX:
        return None

    # Find the first OCP version that supports this operator version
    for ocp_version in sorted(COMPATIBILITY_MATRIX[base_name].keys()):
        supported_versions = COMPATIBILITY_MATRIX[base_name][ocp_version]
        if any(target_version.startswith(v) for v in supported_versions):
            return ocp_version

    return None

def generate_upgrade_path(operator_name, current_version, target_version, current_ocp):
    """Generate detailed upgrade path using ONLY actual versions from compatibility matrix"""
    base_name = operator_name.split('.')[0] if '.' in operator_name else operator_name

    if base_name not in COMPATIBILITY_MATRIX:
        return {
            "steps": [current_version],
            "reason": "Operator not in compatibility matrix",
            "upgrade_type": "Manual"
        }

    current_tuple = version_to_tuple(current_version)
    target_tuple = version_to_tuple(target_version)

    if current_tuple >= target_tuple:
        return {
            "steps": [current_version],
            "reason": f"Current version {current_version} is already at or above target {target_version}",
            "upgrade_type": "None"
        }

    # Check if target version is available in current OCP
    current_ocp_supported = COMPATIBILITY_MATRIX[base_name].get(current_ocp, [])
    target_available_in_current_ocp = any(target_version.startswith(v) for v in current_ocp_supported)

    if not target_available_in_current_ocp:
        # Find which OCP version supports the target operator version
        required_ocp = find_ocp_version_for_operator(operator_name, target_version)

        # Get max available version in current OCP
        max_version_in_current_ocp = current_ocp_supported[-1] if current_ocp_supported else "N/A"

        if required_ocp:
            reason = f"The maximum operator version available in OpenShift {current_ocp} is {max_version_in_current_ocp}. The expected version {target_version} is available from {required_ocp}. So the cluster should be upgraded to {required_ocp} if you want to use {target_version}."
            return {
                "steps": [current_version],
                "reason": reason,
                "upgrade_strategy": "Requires OpenShift Upgrade",
                "required_ocp_version": required_ocp,
                "max_version_in_current_ocp": max_version_in_current_ocp
            }
        else:
            return {
                "steps": [current_version],
                "reason": f"Target version {target_version} is not available in the operator catalog. Please verify the version exists. Maximum version available in OpenShift {current_ocp} is {max_version_in_current_ocp}.",
                "upgrade_strategy": "Manual"
            }

    # Collect ALL available versions from the compatibility matrix
    all_available_versions = set()
    for ocp_version, supported_versions in COMPATIBILITY_MATRIX[base_name].items():
        for version in supported_versions:
            all_available_versions.add(version)

    # Sort versions
    sorted_versions = sorted(all_available_versions, key=version_to_tuple)

    # Find the upgrade path using ONLY available versions
    steps = [current_version]
    current_idx = -1
    target_idx = -1

    for idx, ver in enumerate(sorted_versions):
        if ver.startswith(current_version.split('.')[0] + '.' + current_version.split('.')[1]):
            if version_to_tuple(ver) >= current_tuple:
                current_idx = idx
                break

    for idx, ver in enumerate(sorted_versions):
        if ver.startswith(target_version):
            target_idx = idx
            break

    if current_idx == -1 or target_idx == -1:
        return {
            "steps": [current_version, target_version],
            "reason": f"Target version {target_version} is not available in the operator catalog. Please verify the version exists.",
            "upgrade_type": "Manual"
        }

    # Add intermediate versions
    for idx in range(current_idx + 1, target_idx + 1):
        ver = sorted_versions[idx]
        if ver not in steps:
            steps.append(ver)

    # Build reason based on channel changes
    current_major_minor = f"{current_tuple[0]}.{current_tuple[1]}"
    target_major_minor = f"{target_tuple[0]}.{target_tuple[1]}"

    if current_tuple[0] != target_tuple[0]:
        reason = f"Major version upgrade requires channel change from stable-{current_major_minor} to stable-{target_major_minor}. Manual channel change required in OpenShift Console."
        upgrade_strategy = "Manual (Channel Change Required)"
    elif len(steps) == 2:
        reason = f"Direct upgrade available from {current_version} to {target_version} via OLM skipRange within stable-{current_major_minor} channel"
        upgrade_strategy = "Automatic"
    else:
        reason = f"OLM will automatically upgrade through intermediate versions within stable-{current_major_minor} channel"
        upgrade_strategy = "Automatic"

    return {
        "steps": steps,
        "reason": reason,
        "upgrade_strategy": upgrade_strategy
    }

def check_compatibility(operator_name, current_version, target_ocp):
    """Check operator compatibility"""
    # Extract base operator name
    base_name = operator_name.split('.')[0] if '.' in operator_name else operator_name

    # Get supported versions for target OCP
    supported_versions = []
    if base_name in COMPATIBILITY_MATRIX:
        supported_versions = COMPATIBILITY_MATRIX[base_name].get(target_ocp, [])

    # Always find max supported OCP version for current operator version
    max_ocp = find_max_supported_ocp_version(operator_name, current_version)

    # Check if current version is supported on target OCP
    is_compatible = any(current_version.startswith(v) for v in supported_versions)

    if is_compatible:
        return {
            "operator_name": operator_name,
            "current_version": current_version,
            "status": "compatible",
            "supported_versions": supported_versions,
            "max_supported_ocp": max_ocp,
            "explanation": f"{operator_name} version {current_version} is compatible with OpenShift {target_ocp}. This operator version supports up to OpenShift {max_ocp}.",
            "risk_level": "low"
        }
    else:
        # Not compatible - check if it's incompatible or just needs upgrade

        # supported_versions for target OCP already calculated above
        # Now determine the status based on whether current version is compatible with ANY OCP

        if supported_versions:
            # Target OCP has supported versions
            recommended_version = supported_versions[-1]

            # Check if current version is higher than recommended (prevent downgrades)
            current_ver_tuple = version_to_tuple(current_version)
            recommended_ver_tuple = version_to_tuple(recommended_version)

            if current_ver_tuple >= recommended_ver_tuple:
                # Current version is same or newer than recommended - mark as COMPATIBLE
                return {
                    "operator_name": operator_name,
                    "current_version": current_version,
                    "status": "compatible",
                    "supported_versions": supported_versions,
                    "max_supported_ocp": max_ocp,
                    "explanation": f"{operator_name} version {current_version} is compatible with OpenShift {target_ocp}. This operator version supports up to OpenShift {max_ocp}.",
                    "risk_level": "low"
                }

            if max_ocp and max_ocp < target_ocp:
                # Current version's max OCP is less than target = INCOMPATIBLE + UPGRADE REQUIRED
                return {
                    "operator_name": operator_name,
                    "current_version": current_version,
                    "status": "incompatible_upgrade_required",
                    "supported_versions": supported_versions,
                    "max_supported_ocp": max_ocp,
                    "recommended_version": recommended_version,
                    "explanation": f"{operator_name} version {current_version} is incompatible with OpenShift {target_ocp}. This operator version is compatible with OpenShift {max_ocp} only. Please upgrade the operator to version {recommended_version} for OpenShift {target_ocp} compatibility.",
                    "upgrade_path": f"{current_version} → {recommended_version}",
                    "risk_level": "high"
                }
            else:
                # Current version works on target or newer OCP, just needs operator upgrade
                return {
                    "operator_name": operator_name,
                    "current_version": current_version,
                    "status": "upgrade_required",
                    "target_version": recommended_version,
                    "supported_versions": supported_versions,
                    "max_supported_ocp": max_ocp,
                    "explanation": f"{operator_name} requires upgrade from {current_version} to {recommended_version} for OpenShift {target_ocp}. This operator version supports up to OpenShift {max_ocp}.",
                    "risk_level": "medium"
                }
        elif max_ocp:
            # We know max OCP but no versions for target (operator doesn't support target OCP at all)
            return {
                "operator_name": operator_name,
                "current_version": current_version,
                "status": "incompatible",
                "supported_versions": [],
                "max_supported_ocp": max_ocp,
                "explanation": f"{operator_name} version {current_version} is incompatible with OpenShift {target_ocp}. This operator version is supported up to OpenShift {max_ocp}.",
                "risk_level": "high"
            }
        else:
            # Unknown operator
            return {
                "operator_name": operator_name,
                "current_version": current_version,
                "status": "incompatible",
                "supported_versions": [],
                "explanation": f"{operator_name} version {current_version} is incompatible with OpenShift {target_ocp}. No compatibility information found for this operator.",
                "risk_level": "critical"
            }

def analyze_cluster(request_data):
    """Main analysis function"""
    # Support both old format (5 separate files) and new format (single combined file)
    if "cluster_data" in request_data:
        # New single-file format
        combined_data = request_data["cluster_data"]
        cluster_version = parse_clusterversion(combined_data.get("clusterVersion", {}))
        subscriptions = parse_subscriptions(combined_data.get("subscriptions", {}))
        csvs = parse_csvs(combined_data.get("clusterServiceVersions", {}))
        target_ocp = request_data["target_ocp_version"]
    else:
        # Old format (backward compatibility)
        cluster_version = parse_clusterversion(request_data["clusterversion_json"])
        subscriptions = parse_subscriptions(request_data["subscriptions_json"])
        csvs = parse_csvs(request_data["csv_json"])
        target_ocp = request_data["target_ocp_version"]

    # Map CSVs by name
    csv_map = {csv["name"]: csv for csv in csvs}

    # Get target operator info (optional)
    target_operator = request_data.get("target_operator")
    target_operator_version = request_data.get("target_operator_version")

    # Analyze each subscription
    results = []
    for sub in subscriptions:
        csv_name = sub["current_csv"]
        if csv_name and csv_name in csv_map:
            csv = csv_map[csv_name]
            result = check_compatibility(sub["package"], csv["version"], target_ocp)
            # Add channel information to result
            result["channel"] = sub.get("channel", "N/A")

            # If this is the target operator, generate detailed upgrade path
            if target_operator and target_operator_version and sub["package"] == target_operator:
                result["target_operator_version"] = target_operator_version
                # Extract current cluster OCP version (major.minor only)
                current_cluster_ocp = '.'.join(cluster_version["version"].split('.')[:2])
                result["detailed_upgrade_path"] = generate_upgrade_path(
                    sub["package"],
                    csv["version"],
                    target_operator_version,
                    current_cluster_ocp
                )

            results.append(result)

    # Filter results if target operator is specified
    if target_operator and target_operator_version:
        results = [r for r in results if r["operator_name"] == target_operator]

    # Calculate summary
    compatible_count = sum(1 for r in results if r["status"] == "compatible")
    upgrade_count = sum(1 for r in results if r["status"] in ["upgrade_required", "incompatible_upgrade_required"])
    incompatible_count = sum(1 for r in results if r["status"] in ["incompatible", "incompatible_upgrade_required"])

    # Generate summary
    if incompatible_count > 0:
        risk = "critical"
        summary = f"Critical: {incompatible_count} incompatible operators found. These operator versions are not compatible with the target OpenShift version."
    elif upgrade_count > 2:
        risk = "high"
        summary = f"High Risk: {upgrade_count} operators require upgrades."
    elif upgrade_count > 0:
        risk = "medium"
        summary = f"Medium Risk: {upgrade_count} operators need upgrades."
    else:
        risk = "low"
        summary = "All operators are compatible."

    analysis_id = str(uuid.uuid4())

    response = {
        "analysis_id": analysis_id,
        "timestamp": datetime.now().isoformat(),
        "cluster_info": {
            "current_version": cluster_version["version"],
            "target_version": target_ocp,
            "total_operators": len(results),
            "compatible_count": compatible_count,
            "upgrade_required_count": upgrade_count,
            "unsupported_count": incompatible_count,
            "manual_count": 0,
        },
        "operators": subscriptions,
        "compatibility_results": results,
        "upgrade_paths": {},
        "ai_summary": summary,
        "risk_score": risk
    }

    analysis_cache[analysis_id] = response
    return response

class RequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            # Serve the index.html file
            try:
                html_path = '../index.html'
                with open(html_path, 'r') as f:
                    html_content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(html_content.encode())
            except FileNotFoundError:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'index.html not found')

        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())

        elif self.path.startswith('/api/analysis/'):
            analysis_id = self.path.split('/')[-1]
            if analysis_id in analysis_cache:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(analysis_cache[analysis_id]).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Analysis not found"}).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/analyze':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                # Try to parse as JSON first, then YAML if JSON fails
                raw_data = post_data.decode('utf-8')
                try:
                    request_data = json.loads(raw_data)
                except json.JSONDecodeError:
                    if YAML_SUPPORT:
                        # Try parsing as YAML
                        request_data = yaml.safe_load(raw_data)
                    else:
                        raise ValueError("Invalid JSON and YAML support not available")

                result = analyze_cluster(request_data)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                error_response = {"error": str(e)}
                self.wfile.write(json.dumps(error_response).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"\n🚀 OpenShift Operator Upgrade Advisor Backend")
    print(f"📡 Server running on http://localhost:{port}")
    print(f"📊 API Docs: Check http://localhost:{port}")
    print(f"❤️  Health: http://localhost:{port}/health")
    print(f"\n✅ Ready to analyze OpenShift operators!")
    print(f"Press Ctrl+C to stop\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
