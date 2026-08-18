#!/usr/bin/env python3
"""
Red Hat Documentation & Operator Compatibility MCP Server

This MCP server provides:
1. Access to Red Hat documentation (product docs, KBs, solutions)
2. Operator compatibility data from Red Hat catalogs
3. OpenShift upgrade path information
4. Integration with Red Hat APIs

Similar to Atlassian's remote MCP server approach.
"""

from mcp.server.fastmcp import FastMCP
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import re

# Create MCP server
mcp = FastMCP("Red Hat Documentation & Compatibility")

# Cache configuration
CACHE_DIR = Path.home() / ".cache" / "redhat-mcp"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DURATION = timedelta(hours=24)

# Red Hat API endpoints
REDHAT_API_BASE = "https://access.redhat.com/hydra/rest"
DOCS_SEARCH_API = f"{REDHAT_API_BASE}/search/kcs"
PRODUCT_DOCS_API = "https://docs.redhat.com"

def get_cache_path(cache_key: str) -> Path:
    """Get cache file path for a specific key"""
    safe_key = re.sub(r'[^\w\-]', '_', cache_key)
    return CACHE_DIR / f"{safe_key}.json"

def is_cache_valid(cache_path: Path) -> bool:
    """Check if cache file exists and is still valid"""
    if not cache_path.exists():
        return False
    file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
    return datetime.now() - file_time < CACHE_DURATION

def fetch_with_cache(cache_key: str, fetch_fn, force_refresh: bool = False):
    """Generic caching wrapper"""
    cache_path = get_cache_path(cache_key)

    if not force_refresh and is_cache_valid(cache_path):
        with open(cache_path) as f:
            data = json.load(f)
            data["from_cache"] = True
            return data

    # Fetch fresh data
    data = fetch_fn()
    data["from_cache"] = False
    data["cached_at"] = datetime.now().isoformat()

    # Save to cache
    with open(cache_path, 'w') as f:
        json.dump(data, f, indent=2)

    return data

@mcp.tool()
def search_redhat_docs(
    query: str,
    product: str = None,
    doc_type: str = "all",
    max_results: int = 10
) -> dict:
    """
    Search Red Hat documentation, knowledge base articles, and solutions.

    Args:
        query: Search query (e.g., "OpenShift operator upgrade")
        product: Optional product filter (e.g., "OpenShift Container Platform")
        doc_type: Type of documentation ("all", "solution", "article", "documentation")
        max_results: Maximum number of results to return (default: 10)

    Returns:
        Search results with titles, URLs, and summaries
    """

    try:
        import requests
    except ImportError:
        return {"error": "requests library not installed. Run: pip install requests"}

    cache_key = f"search_{query}_{product}_{doc_type}"

    def fetch():
        try:
            params = {
                "q": query,
                "rows": max_results,
                "documentKind": doc_type if doc_type != "all" else None
            }

            if product:
                params["product"] = product

            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}

            response = requests.get(
                DOCS_SEARCH_API,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            # Parse results
            results = []
            for doc in data.get("response", {}).get("docs", []):
                results.append({
                    "title": doc.get("allTitle", ""),
                    "url": f"https://access.redhat.com{doc.get('uri', '')}",
                    "type": doc.get("documentKind", ""),
                    "product": doc.get("product", []),
                    "summary": doc.get("abstract", ""),
                    "score": doc.get("score", 0)
                })

            return {
                "query": query,
                "product_filter": product,
                "doc_type": doc_type,
                "total_results": len(results),
                "results": results
            }

        except Exception as e:
            return {
                "error": str(e),
                "query": query
            }

    return fetch_with_cache(cache_key, fetch)

@mcp.tool()
def get_operator_documentation(operator_name: str) -> dict:
    """
    Get documentation links for a specific Red Hat operator.

    Args:
        operator_name: Operator name (e.g., "advanced-cluster-management", "openshift-gitops")

    Returns:
        Documentation URLs, installation guides, and release notes
    """

    # Map common operator names to their documentation
    operator_docs_map = {
        "advanced-cluster-management": {
            "product": "Red Hat Advanced Cluster Management for Kubernetes",
            "docs_url": "https://docs.redhat.com/en/documentation/red_hat_advanced_cluster_management_for_kubernetes",
            "operator_hub": "https://operatorhub.io/operator/advanced-cluster-management"
        },
        "openshift-gitops-operator": {
            "product": "Red Hat OpenShift GitOps",
            "docs_url": "https://docs.redhat.com/en/documentation/red_hat_openshift_gitops",
            "operator_hub": "https://operatorhub.io/operator/openshift-gitops-operator"
        },
        "cluster-logging": {
            "product": "Red Hat OpenShift Logging",
            "docs_url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.16/html/logging",
            "operator_hub": "https://operatorhub.io/operator/cluster-logging"
        },
        "elasticsearch-operator": {
            "product": "OpenShift Elasticsearch Operator",
            "docs_url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.16/html/logging",
            "operator_hub": "https://operatorhub.io/operator/elasticsearch-operator"
        }
    }

    if operator_name in operator_docs_map:
        doc_info = operator_docs_map[operator_name]
        doc_info["operator_name"] = operator_name
        doc_info["from_cache"] = False
        return doc_info

    # If not in map, search for it
    search_result = search_redhat_docs(
        query=f"{operator_name} operator documentation",
        product="OpenShift Container Platform",
        max_results=5
    )

    return {
        "operator_name": operator_name,
        "search_results": search_result.get("results", []),
        "operator_hub": f"https://operatorhub.io/operator/{operator_name}",
        "note": "Documentation links from search results"
    }

@mcp.tool()
def get_upgrade_path_documentation(
    source_version: str,
    target_version: str
) -> dict:
    """
    Get OpenShift upgrade path documentation and recommendations.

    Args:
        source_version: Current OpenShift version (e.g., "4.14")
        target_version: Target OpenShift version (e.g., "4.16")

    Returns:
        Upgrade documentation, supported paths, and important notes
    """

    # Search for upgrade documentation
    search_query = f"upgrade OpenShift {source_version} to {target_version}"

    search_results = search_redhat_docs(
        query=search_query,
        product="OpenShift Container Platform",
        doc_type="all",
        max_results=10
    )

    # Add specific documentation links
    major_version = target_version.split('.')[0]
    minor_version = target_version.split('.')[1]

    docs = {
        "source_version": source_version,
        "target_version": target_version,
        "official_docs": {
            "upgrade_guide": f"https://docs.redhat.com/en/documentation/openshift_container_platform/{target_version}/html/updating_clusters",
            "release_notes": f"https://docs.redhat.com/en/documentation/openshift_container_platform/{target_version}/html/release_notes",
            "operator_compatibility": f"https://access.redhat.com/labs/ocpouic/?upgrade_path={source_version}%20to%20{target_version}"
        },
        "search_results": search_results.get("results", []),
        "important_links": [
            {
                "title": "OCP Update Graph Tool",
                "url": "https://access.redhat.com/labs/ocpupgradegraph/update_path"
            },
            {
                "title": "Operator Compatibility",
                "url": "https://access.redhat.com/labs/ocpouic/"
            }
        ]
    }

    return docs

@mcp.tool()
def get_product_documentation(product_name: str, version: str = None) -> dict:
    """
    Get documentation for a Red Hat product.

    Args:
        product_name: Product name (e.g., "OpenShift Container Platform", "RHEL")
        version: Optional version (e.g., "4.16", "9")

    Returns:
        Documentation links and resources
    """

    products = {
        "OpenShift Container Platform": {
            "base_url": "https://docs.redhat.com/en/documentation/openshift_container_platform",
            "latest": "4.16",
            "categories": ["Installing", "Updating clusters", "Operators", "Networking", "Storage"]
        },
        "Red Hat Enterprise Linux": {
            "base_url": "https://docs.redhat.com/en/documentation/red_hat_enterprise_linux",
            "latest": "9",
            "categories": ["Installing", "Configuring", "Managing", "Security"]
        },
        "Red Hat Advanced Cluster Management": {
            "base_url": "https://docs.redhat.com/en/documentation/red_hat_advanced_cluster_management_for_kubernetes",
            "latest": "2.11",
            "categories": ["Installing", "Clusters", "Applications", "Governance"]
        }
    }

    if product_name in products:
        product = products[product_name]
        version_to_use = version or product["latest"]

        return {
            "product": product_name,
            "version": version_to_use,
            "documentation_url": f"{product['base_url']}/{version_to_use}",
            "categories": product["categories"],
            "latest_version": product["latest"]
        }

    # Search if not in predefined list
    search_results = search_redhat_docs(
        query=f"{product_name} documentation",
        max_results=5
    )

    return {
        "product": product_name,
        "version": version,
        "search_results": search_results.get("results", [])
    }

@mcp.resource("redhat://docs/popular")
def get_popular_docs() -> str:
    """
    Get list of popular Red Hat documentation resources.
    """

    popular = {
        "OpenShift": [
            {
                "title": "Installing OpenShift",
                "url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.16/html/installing"
            },
            {
                "title": "Updating clusters",
                "url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.16/html/updating_clusters"
            },
            {
                "title": "Operators",
                "url": "https://docs.redhat.com/en/documentation/openshift_container_platform/4.16/html/operators"
            }
        ],
        "Operators": [
            {
                "title": "Operator Update Information Checker",
                "url": "https://access.redhat.com/labs/ocpouic/"
            },
            {
                "title": "OperatorHub.io",
                "url": "https://operatorhub.io/"
            }
        ],
        "Tools": [
            {
                "title": "OpenShift Upgrade Graph",
                "url": "https://access.redhat.com/labs/ocpupgradegraph/"
            },
            {
                "title": "Product Life Cycles",
                "url": "https://access.redhat.com/product-life-cycles"
            }
        ]
    }

    return json.dumps(popular, indent=2)

@mcp.resource("redhat://server/info")
def get_server_info() -> str:
    """
    Get MCP server information.
    """

    try:
        import requests
        has_requests = True
    except ImportError:
        has_requests = False

    info = {
        "server": "Red Hat Documentation & Compatibility MCP Server",
        "version": "1.0.0",
        "description": "Access Red Hat documentation, operator compatibility, and upgrade paths",
        "data_sources": [
            "https://access.redhat.com (Knowledge Base, Solutions, Articles)",
            "https://docs.redhat.com (Product Documentation)",
            "https://operatorhub.io (Operator Documentation)"
        ],
        "cache_dir": str(CACHE_DIR),
        "cache_duration_hours": CACHE_DURATION.total_seconds() / 3600,
        "dependencies": {
            "requests_installed": has_requests
        },
        "tools": [
            "search_redhat_docs - Search all Red Hat documentation",
            "get_operator_documentation - Get operator-specific docs",
            "get_upgrade_path_documentation - Get upgrade guides",
            "get_product_documentation - Get product documentation"
        ]
    }

    return json.dumps(info, indent=2)

if __name__ == "__main__":
    print("=" * 80)
    print("Red Hat Documentation & Compatibility MCP Server")
    print("=" * 80)
    print()
    print("This MCP server provides access to:")
    print("  • Red Hat Knowledge Base articles and solutions")
    print("  • Product documentation (OpenShift, RHEL, etc.)")
    print("  • Operator documentation and compatibility info")
    print("  • Upgrade path documentation and tools")
    print()
    print("Setup:")
    print("  pip install fastmcp requests")
    print()
    print("Tools:")
    print("  - search_redhat_docs(query, product, doc_type)")
    print("  - get_operator_documentation(operator_name)")
    print("  - get_upgrade_path_documentation(source_version, target_version)")
    print("  - get_product_documentation(product_name, version)")
    print()
    print("Resources:")
    print("  - redhat://docs/popular - Popular documentation links")
    print("  - redhat://server/info - Server information")
    print()
    print("=" * 80)
    print()

    # Run the MCP server
    mcp.run()
