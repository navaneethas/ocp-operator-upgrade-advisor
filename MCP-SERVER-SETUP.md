# Red Hat Documentation MCP Server Setup

This guide shows you how to set up and use the Red Hat Documentation MCP Server with Claude.

## What is This?

An **MCP (Model Context Protocol) server** that gives Claude direct access to:
- ✅ Red Hat documentation search
- ✅ Operator compatibility information  
- ✅ OpenShift upgrade path documentation
- ✅ Product documentation (OpenShift, RHEL, ACM, etc.)

**Similar to [Atlassian's remote MCP server](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)**

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install fastmcp requests
```

### 2. Test the Server

```bash
python redhat-docs-mcp-server.py
```

You should see:
```
================================================================================
Red Hat Documentation & Compatibility MCP Server
================================================================================

This MCP server provides access to:
  • Red Hat Knowledge Base articles and solutions
  • Product documentation (OpenShift, RHEL, etc.)
  • Operator documentation and compatibility info
  • Upgrade path documentation and tools
...
```

### 3. Configure Claude to Use the MCP Server

Add to your Claude config file (`~/.claude/config.json` or Claude Desktop settings):

```json
{
  "mcpServers": {
    "redhat-docs": {
      "command": "python",
      "args": ["/Users/nsenthil/AI_TOOL/openshift-upgrade-advisor/redhat-docs-mcp-server.py"]
    }
  }
}
```

**For Claude Desktop (Mac):**
1. Open Claude Desktop
2. Go to Settings → Developer → Edit Config
3. Add the MCP server configuration above
4. Restart Claude Desktop

**For Claude CLI:**
Config location: `~/.claude/config.json`

### 4. Verify Connection

In Claude, ask:
```
Can you search Red Hat docs for "OpenShift operator upgrade"?
```

Claude will use the `search_redhat_docs` tool automatically! 🎉

---

## 📚 Available Tools

### 1. `search_redhat_docs`

Search Red Hat documentation, knowledge base, and solutions.

**Example:**
```
Search Red Hat docs for "OpenShift 4.16 networking"
```

**Parameters:**
- `query` - Search query
- `product` - Filter by product (optional)
- `doc_type` - Type: "all", "solution", "article", "documentation"
- `max_results` - Max results (default: 10)

### 2. `get_operator_documentation`

Get documentation for a specific operator.

**Example:**
```
Get documentation for advanced-cluster-management operator
```

**Parameters:**
- `operator_name` - Operator name (e.g., "openshift-gitops-operator")

### 3. `get_upgrade_path_documentation`

Get OpenShift upgrade documentation and paths.

**Example:**
```
Get upgrade documentation from OpenShift 4.14 to 4.16
```

**Parameters:**
- `source_version` - Current version (e.g., "4.14")
- `target_version` - Target version (e.g., "4.16")

### 4. `get_product_documentation`

Get documentation for Red Hat products.

**Example:**
```
Get documentation for OpenShift Container Platform version 4.16
```

**Parameters:**
- `product_name` - Product name
- `version` - Version (optional, defaults to latest)

---

## 🔧 Advanced Configuration

### Caching

The server caches results for **24 hours** in `~/.cache/redhat-mcp/`

**Clear cache:**
```bash
rm -rf ~/.cache/redhat-mcp/
```

### Custom Cache Duration

Edit `redhat-docs-mcp-server.py`:

```python
CACHE_DURATION = timedelta(hours=24)  # Change to hours=12, days=1, etc.
```

---

## 🎯 Usage Examples

### Example 1: Search for Operator Upgrade Info

**You ask Claude:**
> "Search Red Hat docs for how to upgrade the GitOps operator"

**Claude calls:**
```python
search_redhat_docs(
    query="upgrade GitOps operator",
    product="OpenShift Container Platform",
    doc_type="all"
)
```

**Response:**
```json
{
  "query": "upgrade GitOps operator",
  "total_results": 5,
  "results": [
    {
      "title": "Upgrading Red Hat OpenShift GitOps",
      "url": "https://access.redhat.com/documentation/...",
      "type": "documentation",
      "summary": "..."
    }
  ]
}
```

### Example 2: Get Upgrade Path Documentation

**You ask Claude:**
> "What's the upgrade path from OpenShift 4.14 to 4.16?"

**Claude calls:**
```python
get_upgrade_path_documentation(
    source_version="4.14",
    target_version="4.16"
)
```

**Response:**
```json
{
  "source_version": "4.14",
  "target_version": "4.16",
  "official_docs": {
    "upgrade_guide": "https://docs.redhat.com/.../updating_clusters",
    "release_notes": "https://docs.redhat.com/.../release_notes",
    "operator_compatibility": "https://access.redhat.com/labs/ocpouic/..."
  },
  "search_results": [...]
}
```

### Example 3: Get Operator Documentation

**You ask Claude:**
> "Show me documentation for the ACM operator"

**Claude calls:**
```python
get_operator_documentation(
    operator_name="advanced-cluster-management"
)
```

**Response:**
```json
{
  "operator_name": "advanced-cluster-management",
  "product": "Red Hat Advanced Cluster Management for Kubernetes",
  "docs_url": "https://docs.redhat.com/en/documentation/...",
  "operator_hub": "https://operatorhub.io/operator/advanced-cluster-management"
}
```

---

## 🔄 Workflow: Natural Conversation with Claude

```
You: "I need to upgrade my OpenShift cluster from 4.14 to 4.16. 
      What operators might have compatibility issues?"

Claude: *Calls get_upgrade_path_documentation()*
        *Calls search_redhat_docs("operator compatibility 4.14 4.16")*
        
        "Based on Red Hat documentation, here's what you need to check:
        
        1. Review the operator compatibility checker: 
           https://access.redhat.com/labs/ocpouic/?upgrade_path=4.14%20to%204.16
        
        2. Key operators to verify:
           - Advanced Cluster Management
           - OpenShift GitOps
           - Logging/Elasticsearch
        
        3. Upgrade guide: https://docs.redhat.com/.../updating_clusters
        
        Would you like me to check specific operators?"

You: "Yes, check the ACM operator"

Claude: *Calls get_operator_documentation("advanced-cluster-management")*
        
        "ACM documentation: https://docs.redhat.com/en/documentation/...
        
        For OpenShift 4.16, you'll need ACM 2.9 or later.
        Current ACM upgrade paths: ..."
```

---

## 🆚 Comparison: MCP Server vs Manual Method

| Feature | MCP Server | Manual oc-mirror |
|---------|-----------|------------------|
| Setup | Install once, use everywhere | Run scripts each time |
| Data Source | Red Hat API | Registry queries |
| Updates | Auto-cached (24h) | Manual collection |
| Integration | Works in Claude naturally | Requires file upload |
| Speed | Fast (cached) | Slow (20-30 min per version) |
| Coverage | Official docs + compatibility | Raw catalog data |
| Authentication | Optional | Registry login required |

**Recommendation:**
- **Use MCP Server for:** Quick lookups, documentation, general compatibility checks
- **Use oc-mirror for:** Detailed version-by-version data, air-gapped environments

---

## 🐛 Troubleshooting

### Issue: "MCP server not responding"

**Solution:**
1. Check if server is running: `python redhat-docs-mcp-server.py`
2. Verify config path in `~/.claude/config.json`
3. Restart Claude Desktop

### Issue: "requests library not installed"

**Solution:**
```bash
pip install requests
```

### Issue: "Cache is stale"

**Solution:**
Clear cache:
```bash
rm -rf ~/.cache/redhat-mcp/
```

---

## 📝 Adding More Operators

Edit `operator_docs_map` in `redhat-docs-mcp-server.py`:

```python
operator_docs_map = {
    "your-operator-name": {
        "product": "Your Operator Product Name",
        "docs_url": "https://docs.redhat.com/...",
        "operator_hub": "https://operatorhub.io/operator/your-operator"
    }
}
```

---

## 🔐 Optional: Authentication (Future Enhancement)

For accessing authenticated Red Hat APIs:

```bash
export REDHAT_API_TOKEN="your_token_here"
```

Then modify the server to include:
```python
headers = {
    "Authorization": f"Bearer {os.getenv('REDHAT_API_TOKEN')}"
}
```

---

## 🎯 Next Steps

1. ✅ Install the MCP server
2. ✅ Configure Claude to use it
3. ✅ Test with a query
4. ✅ Integrate with your upgrade workflow

**Combined Workflow:**
1. Use MCP server for initial research and documentation
2. Use oc-mirror for detailed version collection
3. Use analyzer with both data sources for comprehensive results

---

## 📚 Resources

- **MCP Protocol:** https://modelcontextprotocol.io/
- **FastMCP Library:** https://github.com/jlowin/fastmcp
- **Red Hat Documentation:** https://docs.redhat.com/
- **Red Hat API:** https://access.redhat.com/documentation/en-us/red_hat_customer_portal/1/html/red_hat_customer_portal_api_guide/

---

**Need help?** The MCP server includes a built-in info resource:

Ask Claude: `Show me the Red Hat MCP server info`

Claude will call: `redhat://server/info`
