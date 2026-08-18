#!/usr/bin/env python3
"""
MCP Server for Red Hat OCP Operator Update Information Checker
Fetches operator compatibility data from https://access.redhat.com/labs/ocpouic/

This server uses browser automation to:
1. Login to Red Hat Customer Portal
2. Navigate to OCP Operator Update Information Checker
3. Extract compatibility data
4. Cache and serve it via MCP tools
"""

from mcp.server.fastmcp import FastMCP
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import subprocess
import tempfile

# Create MCP server
mcp = FastMCP("Red Hat OCP Operator Compatibility")

# Cache configuration
CACHE_DIR = Path.home() / ".cache" / "redhat-ocpouic"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DURATION = timedelta(days=1)  # Cache for 24 hours

def get_cache_path(source_ocp: str, target_ocp: str) -> Path:
    """Get cache file path for a specific upgrade path"""
    return CACHE_DIR / f"compat_{source_ocp}_to_{target_ocp}.json"

def is_cache_valid(cache_path: Path) -> bool:
    """Check if cache file exists and is still valid"""
    if not cache_path.exists():
        return False

    # Check if cache is expired
    file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
    if datetime.now() - file_time > CACHE_DURATION:
        return False

    return True

def fetch_compatibility_data_selenium(source_ocp: str, target_ocp: str) -> Dict:
    """
    Fetch compatibility data using Selenium browser automation
    Requires: pip install selenium
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        return {
            "error": "Selenium not installed. Run: pip install selenium",
            "method": "selenium"
        }

    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the tool
        url = f"https://access.redhat.com/labs/ocpouic/?upgrade_path={source_ocp}%20to%20{target_ocp}"
        driver.get(url)

        # Wait for login or data to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Check if login required
        if "login" in driver.current_url.lower() or "sso" in driver.current_url.lower():
            # Get credentials from environment
            username = os.getenv("REDHAT_USERNAME")
            password = os.getenv("REDHAT_PASSWORD")

            if not username or not password:
                driver.quit()
                return {
                    "error": "Login required. Set REDHAT_USERNAME and REDHAT_PASSWORD environment variables",
                    "login_url": driver.current_url
                }

            # Perform login (this varies based on Red Hat SSO implementation)
            # You may need to adjust selectors
            username_field = driver.find_element(By.ID, "username")
            password_field = driver.find_element(By.ID, "password")
            username_field.send_keys(username)
            password_field.send_keys(password)

            login_button = driver.find_element(By.ID, "submit")
            login_button.click()

            # Wait for redirect back to tool
            time.sleep(5)

        # Wait for data to load
        time.sleep(5)

        # Extract page content or API calls
        # Option 1: Parse HTML directly
        page_source = driver.page_source

        # Option 2: Capture network requests (requires additional setup)
        # You can use browser DevTools Protocol to capture API calls

        driver.quit()

        return {
            "source_ocp": source_ocp,
            "target_ocp": target_ocp,
            "fetched_at": datetime.now().isoformat(),
            "data": page_source,
            "method": "selenium"
        }

    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        return {
            "error": str(e),
            "method": "selenium"
        }

def fetch_compatibility_data_api(source_ocp: str, target_ocp: str) -> Dict:
    """
    Fetch compatibility data by reverse-engineering the API
    This is more reliable if we can identify the API endpoint
    """
    try:
        import requests
    except ImportError:
        return {
            "error": "requests not installed. Run: pip install requests"
        }

    # Try to find the API endpoint
    # You'll need to inspect the browser's Network tab to find this
    api_url = "https://access.redhat.com/labs/ocpouic/api/check"  # Example - adjust based on actual API

    # May need authentication
    session = requests.Session()

    # Check if we have saved session cookie
    cookie_file = CACHE_DIR / "redhat_session.json"
    if cookie_file.exists():
        with open(cookie_file) as f:
            cookies = json.load(f)
            session.cookies.update(cookies)

    try:
        response = session.get(
            api_url,
            params={
                "source_version": source_ocp,
                "target_version": target_ocp
            }
        )

        if response.status_code == 401:
            return {
                "error": "Authentication required",
                "method": "api"
            }

        response.raise_for_status()
        return {
            "source_ocp": source_ocp,
            "target_ocp": target_ocp,
            "fetched_at": datetime.now().isoformat(),
            "data": response.json(),
            "method": "api"
        }

    except Exception as e:
        return {
            "error": str(e),
            "method": "api"
        }

def fetch_compatibility_data(source_ocp: str, target_ocp: str, force_refresh: bool = False) -> Dict:
    """
    Main function to fetch compatibility data with caching
    """
    cache_path = get_cache_path(source_ocp, target_ocp)

    # Check cache first
    if not force_refresh and is_cache_valid(cache_path):
        with open(cache_path) as f:
            cached_data = json.load(f)
            cached_data["from_cache"] = True
            return cached_data

    # Try API method first (faster)
    data = fetch_compatibility_data_api(source_ocp, target_ocp)

    # Fallback to Selenium if API fails
    if "error" in data:
        print(f"API method failed: {data['error']}, trying Selenium...")
        data = fetch_compatibility_data_selenium(source_ocp, target_ocp)

    # Cache the result
    if "error" not in data:
        with open(cache_path, 'w') as f:
            json.dump(data, f, indent=2)
        data["from_cache"] = False

    return data

@mcp.tool()
def check_upgrade_compatibility(
    source_ocp_version: str,
    target_ocp_version: str,
    operator_name: str = None
) -> dict:
    """
    Check operator compatibility for an OpenShift upgrade path.

    Args:
        source_ocp_version: Current OpenShift version (e.g., "4.14")
        target_ocp_version: Target OpenShift version (e.g., "4.16")
        operator_name: Optional - specific operator to check

    Returns:
        Compatibility information including incompatible operators and recommendations
    """

    data = fetch_compatibility_data(source_ocp_version, target_ocp_version)

    if "error" in data:
        return {
            "status": "error",
            "error": data["error"],
            "recommendation": "Please ensure you have set REDHAT_USERNAME and REDHAT_PASSWORD environment variables, or use oc-mirror method instead."
        }

    # Parse the data (structure depends on what we extract)
    result = {
        "source_version": source_ocp_version,
        "target_version": target_ocp_version,
        "checked_at": data.get("fetched_at"),
        "from_cache": data.get("from_cache", False),
        "method": data.get("method", "unknown")
    }

    # If we have parsed operator data
    if "operators" in data.get("data", {}):
        operators = data["data"]["operators"]

        if operator_name:
            # Filter for specific operator
            operators = [op for op in operators if op["name"] == operator_name]

        result["operators"] = operators
        result["incompatible_count"] = len([op for op in operators if not op.get("compatible")])

    return result

@mcp.tool()
def get_cached_upgrade_paths() -> dict:
    """
    List all cached upgrade path data.

    Returns:
        List of cached upgrade paths with metadata
    """

    cached_files = list(CACHE_DIR.glob("compat_*.json"))

    results = []
    for cache_file in cached_files:
        # Extract source and target from filename
        # Format: compat_4.14_to_4.16.json
        parts = cache_file.stem.replace("compat_", "").replace("_to_", " ").split()
        if len(parts) == 2:
            source, target = parts
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            is_valid = is_cache_valid(cache_file)

            results.append({
                "source_version": source,
                "target_version": target,
                "cached_at": file_time.isoformat(),
                "is_valid": is_valid,
                "file_size_kb": cache_file.stat().st_size / 1024
            })

    return {
        "cache_dir": str(CACHE_DIR),
        "total_cached": len(results),
        "cached_paths": results
    }

@mcp.tool()
def clear_cache(source_ocp_version: str = None, target_ocp_version: str = None) -> dict:
    """
    Clear cached compatibility data.

    Args:
        source_ocp_version: Optional - clear specific source version
        target_ocp_version: Optional - clear specific target version

    Returns:
        Summary of cleared cache entries
    """

    if source_ocp_version and target_ocp_version:
        # Clear specific cache
        cache_path = get_cache_path(source_ocp_version, target_ocp_version)
        if cache_path.exists():
            cache_path.unlink()
            return {
                "status": "cleared",
                "path": f"{source_ocp_version} to {target_ocp_version}"
            }
        else:
            return {
                "status": "not_found",
                "path": f"{source_ocp_version} to {target_ocp_version}"
            }
    else:
        # Clear all cache
        cached_files = list(CACHE_DIR.glob("compat_*.json"))
        count = len(cached_files)

        for cache_file in cached_files:
            cache_file.unlink()

        return {
            "status": "cleared",
            "cleared_count": count
        }

@mcp.resource("redhat://compatibility/info")
def get_server_info() -> str:
    """
    Get MCP server information and configuration.
    """

    has_selenium = False
    try:
        import selenium
        has_selenium = True
    except ImportError:
        pass

    has_requests = False
    try:
        import requests
        has_requests = True
    except ImportError:
        pass

    has_credentials = bool(os.getenv("REDHAT_USERNAME") and os.getenv("REDHAT_PASSWORD"))

    info = {
        "server": "Red Hat OCP Operator Compatibility MCP Server",
        "version": "1.0.0",
        "data_source": "https://access.redhat.com/labs/ocpouic/",
        "cache_dir": str(CACHE_DIR),
        "cache_duration_hours": CACHE_DURATION.total_seconds() / 3600,
        "dependencies": {
            "selenium_installed": has_selenium,
            "requests_installed": has_requests,
            "redhat_credentials_configured": has_credentials
        },
        "setup_instructions": {
            "install_selenium": "pip install selenium",
            "install_requests": "pip install requests",
            "set_credentials": "export REDHAT_USERNAME='your_email' && export REDHAT_PASSWORD='your_password'"
        }
    }

    return json.dumps(info, indent=2)

if __name__ == "__main__":
    print("=" * 80)
    print("Red Hat OCP Operator Compatibility MCP Server")
    print("=" * 80)
    print()
    print("This MCP server fetches operator compatibility data from:")
    print("https://access.redhat.com/labs/ocpouic/")
    print()
    print("Setup:")
    print("  1. pip install selenium requests")
    print("  2. export REDHAT_USERNAME='your_email'")
    print("  3. export REDHAT_PASSWORD='your_password'")
    print()
    print("Tools:")
    print("  - check_upgrade_compatibility(source_ocp, target_ocp, operator_name)")
    print("  - get_cached_upgrade_paths()")
    print("  - clear_cache(source_ocp, target_ocp)")
    print()
    print("=" * 80)
    print()

    # Run the MCP server
    mcp.run()
