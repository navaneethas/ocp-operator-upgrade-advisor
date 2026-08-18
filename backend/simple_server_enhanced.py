#!/usr/bin/env python3
"""
Enhanced OpenShift Operator Upgrade Advisor Server
Uses real compatibility matrix from oc-mirror data
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import re
from datetime import datetime
import uuid
from pathlib import Path

# Try to import YAML support (optional)
try:
    import yaml
    YAML_SUPPORT = True
except ImportError:
    YAML_SUPPORT = False

# Load compatibility matrix
def load_compatibility_matrix():
    """Load compatibility matrix from JSON file"""
    locations = [
        Path(__file__).parent.parent / "compatibility_matrix.json",
        Path("../compatibility_matrix.json"),
        Path("compatibility_matrix.json"),
    ]

    for location in locations:
        if location.exists():
            with open(location, 'r') as f:
                return json.load(f)

    print("WARNING: compatibility_matrix.json not found, using empty matrix")
    return {}

COMPATIBILITY_MATRIX = load_compatibility_matrix()
print(f"Loaded compatibility matrix with {len(COMPATIBILITY_MATRIX)} operators")

# Simple in-memory storage
analysis_cache = {}

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
            "source": spec.get("source", ""),
            "source_namespace": spec.get("sourceNamespace", ""),
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

    for ocp_version in sorted(operator_data.keys(), reverse=True):
        supported_versions = operator_data[ocp_version]
        if normalized_version in supported_versions:
            max_ocp_version = ocp_version
            break

    return max_ocp_version

def check_compatibility(operator_name, current_version, target_ocp, catalog_source=None):
    """Check operator compatibility"""

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
                    "explanation": f"Sorry, this operator is from {catalog_type}. The compatibility checker is currently designed for Red Hat operators only. Please check the operator's documentation for compatibility information.",
                }

    if operator_name not in COMPATIBILITY_MATRIX:
        return {
            "operator_name": operator_name,
            "current_version": current_version,
            "status": "unknown",
            "supported_versions": [],
            "max_supported_ocp": None,
            "explanation": f"No compatibility data available for {operator_name}. This may be a community, certified, or custom operator. The compatibility checker is designed for Red Hat operators only.",
        }

    # Normalize the current version (remove build metadata)
    normalized_version = normalize_version(current_version)

    supported_versions = COMPATIBILITY_MATRIX[operator_name].get(target_ocp, [])
    max_ocp = find_max_supported_ocp_version(operator_name, current_version)
    is_compatible = normalized_version in supported_versions

    if is_compatible:
        return {
            "operator_name": operator_name,
            "current_version": current_version,
            "status": "compatible",
            "supported_versions": supported_versions,
            "max_supported_ocp": max_ocp,
            "explanation": f"{operator_name} v{current_version} is compatible with OpenShift {target_ocp}. Supported up to OCP {max_ocp}.",
        }
    else:
        if supported_versions:
            recommended_version = supported_versions[-1]
            return {
                "operator_name": operator_name,
                "current_version": current_version,
                "status": "incompatible_upgrade_required",
                "supported_versions": supported_versions,
                "max_supported_ocp": max_ocp,
                "recommended_version": recommended_version,
                "explanation": f"{operator_name} v{current_version} is only supported up to OCP {max_ocp}. Target OCP {target_ocp} requires upgrade to v{recommended_version}.",
            }
        else:
            return {
                "operator_name": operator_name,
                "current_version": current_version,
                "status": "incompatible",
                "supported_versions": [],
                "max_supported_ocp": max_ocp,
                "explanation": f"{operator_name} v{current_version} not available in OpenShift {target_ocp} catalog.",
            }

def analyze_cluster(request_data):
    """Main analysis function"""
    if "cluster_data" in request_data:
        combined_data = request_data["cluster_data"]
        cluster_version = parse_clusterversion(combined_data.get("clusterVersion", {}))
        subscriptions = parse_subscriptions(combined_data.get("subscriptions", {}))
        csvs = parse_csvs(combined_data.get("clusterServiceVersions", {}))
        target_ocp = request_data["target_ocp_version"]
    else:
        cluster_version = parse_clusterversion(request_data["clusterversion_json"])
        subscriptions = parse_subscriptions(request_data["subscriptions_json"])
        csvs = parse_csvs(request_data["csv_json"])
        target_ocp = request_data["target_ocp_version"]

    csv_map = {csv["name"]: csv for csv in csvs}
    target_operator = request_data.get("target_operator")
    target_operator_version = request_data.get("target_operator_version")

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
            result["target_ocp"] = target_ocp  # Add for UI display
            results.append(result)

    if target_operator and target_operator_version:
        results = [r for r in results if r["operator_name"] == target_operator]

    compatible_count = sum(1 for r in results if r["status"] == "compatible")
    upgrade_count = sum(1 for r in results if r["status"] in ["upgrade_required", "incompatible_upgrade_required"])
    incompatible_count = sum(1 for r in results if r["status"] == "incompatible")
    unknown_count = sum(1 for r in results if r["status"] == "unknown")

    if incompatible_count > 0 or unknown_count > 0:
        risk = "critical"
        summary = f"Critical: {incompatible_count + unknown_count} operators need attention."
    elif upgrade_count > 2:
        risk = "high"
        summary = f"High: {upgrade_count} operators require upgrades."
    elif upgrade_count > 0:
        risk = "medium"
        summary = f"Medium: {upgrade_count} operators need upgrades."
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
            "unknown_count": unknown_count,
        },
        "operators": subscriptions,
        "compatibility_results": results,
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
            self.wfile.write(json.dumps({"status": "healthy", "operators": len(COMPATIBILITY_MATRIX)}).encode())

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
                raw_data = post_data.decode('utf-8')
                try:
                    request_data = json.loads(raw_data)
                except json.JSONDecodeError:
                    if YAML_SUPPORT:
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
    print(f"\n🚀 OpenShift Operator Upgrade Advisor Backend (Enhanced)")
    print(f"📡 Server running on http://localhost:{port}")
    print(f"📊 Loaded {len(COMPATIBILITY_MATRIX)} operators")
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
