# OpenShift Operator Upgrade Advisor

A powerful tool to analyze OpenShift operator compatibility and generate upgrade paths. Available in both **Web UI** (for JSON) and **CLI** (for YAML) modes.

## 🎯 Features

- ✅ Check operator compatibility with target OpenShift versions
- 🔍 Analyze installed operators from cluster data
- 📊 Generate detailed upgrade paths
- 🎨 Web UI for JSON format analysis
- 💻 CLI for terminal-based YAML analysis (perfect for supportshell environments)
- 📈 Risk assessment and recommendations

---

## 🖥️ Web UI Mode (JSON Format)

### Prerequisites
- Python 3.7+
- Modern web browser

### Quick Start

1. **Start the backend server:**
```bash
cd backend
python3 simple_server.py
```

2. **Open your browser:**
```
http://localhost:8000
```

3. **Collect cluster data** (run on OpenShift cluster):
```bash
(echo '{"cluster_data":'; \
 echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; \
 echo '  "subscriptions":'; oc get sub -A -o json; echo ','; \
 echo '  "clusterServiceVersions":'; oc get csv -A -o json; echo ','; \
 echo '  "catalogSources":'; oc get catalogsource -A -o json; echo ','; \
 echo '  "packageManifests":'; oc get packagemanifest -o json; \
 echo '}') | jq > openshift-data.json
```

4. **Upload and analyze:**
   - Upload `openshift-data.json` via the web UI
   - Select target OpenShift version
   - Click "Analyze Operators"
   - View detailed compatibility results

---

## 💻 CLI Mode (YAML Format)

Perfect for **supportshell** and **must-gather** environments where you can't transfer files or access a browser.

### Prerequisites
- Python 3.7+
- PyYAML (`pip3 install pyyaml`)

### Quick Start

1. **Collect cluster data** (run on OpenShift cluster or supportshell):
```bash
(echo 'cluster_data:'; \
 echo '  clusterVersion:'; oc get clusterversion version -o yaml | sed 's/^/    /'; \
 echo '  subscriptions:'; oc get sub -A -o yaml | sed 's/^/    /'; \
 echo '  clusterServiceVersions:'; oc get csv -A -o yaml | sed 's/^/    /'; \
 echo '  catalogSources:'; oc get catalogsource -A -o yaml | sed 's/^/    /'; \
 echo '  packageManifests:'; oc get packagemanifest -o yaml | sed 's/^/    /') > openshift-data.yaml
```

2. **Copy the CLI analyzer to your supportshell:**
```bash
# Transfer cli-analyzer.py to your supportshell environment
scp cli-analyzer.py user@supportshell:/tmp/
```

3. **Run the analysis:**
```bash
python3 cli-analyzer.py openshift-data.yaml --target-ocp 4.21
```

Or interactively:
```bash
python3 cli-analyzer.py openshift-data.yaml
# You'll be prompted to enter the target OCP version
```

### CLI Output

The CLI provides color-coded terminal output:
- 🟢 **Green**: Compatible operators
- 🟡 **Yellow**: Operators requiring upgrades
- 🔴 **Red**: Incompatible operators
- Detailed explanations for each operator
- Risk assessment summary
- Recommended upgrade versions

---

## 📋 Supported Operators

The tool currently tracks compatibility for:
- **OpenShift GitOps** (gitops-operator)
- **Quay** (quay-operator)
- **Cluster Logging** (cluster-logging)
- **OpenShift Pipelines** (openshift-pipelines-operator-rh)
- **Advanced Cluster Management** (advanced-cluster-management)
- **Service Mesh** (servicemeshoperator3)

Supports OpenShift versions: **4.12 - 4.22**

---

## 🔧 Usage Examples

### Web UI Example
```bash
# 1. Start backend
cd backend && python3 simple_server.py

# 2. Collect data from cluster
(echo '{"cluster_data":'; \
 echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; \
 echo '  "subscriptions":'; oc get sub -A -o json; echo ','; \
 echo '  "clusterServiceVersions":'; oc get csv -A -o json; echo ','; \
 echo '  "catalogSources":'; oc get catalogsource -A -o json; echo ','; \
 echo '  "packageManifests":'; oc get packagemanifest -o json; \
 echo '}') | jq > openshift-data.json

# 3. Open http://localhost:8000 and upload the file
```

### CLI Example (Supportshell)
```bash
# 1. Collect data in supportshell
(echo 'cluster_data:'; \
 echo '  clusterVersion:'; oc get clusterversion version -o yaml | sed 's/^/    /'; \
 echo '  subscriptions:'; oc get sub -A -o yaml | sed 's/^/    /'; \
 echo '  clusterServiceVersions:'; oc get csv -A -o yaml | sed 's/^/    /'; \
 echo '  catalogSources:'; oc get catalogsource -A -o yaml | sed 's/^/    /'; \
 echo '  packageManifests:'; oc get packagemanifest -o yaml | sed 's/^/    /') > openshift-data.yaml

# 2. Run analysis
python3 cli-analyzer.py openshift-data.yaml --target-ocp 4.21
```

---

## 🗂️ File Formats

### JSON Format (Web UI)
```json
{
  "cluster_data": {
    "clusterVersion": {...},
    "subscriptions": {...},
    "clusterServiceVersions": {...},
    "catalogSources": {...},
    "packageManifests": {...}
  }
}
```

### YAML Format (CLI)
```yaml
cluster_data:
  clusterVersion:
    spec:
      channel: stable-4.19
    status:
      desired:
        version: 4.19.8
  subscriptions:
    items:
      - metadata:
          name: acm-subscription
        spec:
          name: advanced-cluster-management
        status:
          currentCSV: advanced-cluster-management.v2.13.9
  clusterServiceVersions:
    items: [...]
  catalogSources:
    items: [...]
  packageManifests:
    items: [...]
```

---

## 🚀 Deployment

### Local Development
```bash
# Backend
cd backend
python3 simple_server.py

# Access UI
open http://localhost:8000
```

### Production
```bash
# Build and run with Docker
docker build -t ocp-upgrade-advisor .
docker run -p 8000:8000 ocp-upgrade-advisor
```

---

## 🤝 Use Cases

### Use Case 1: Desktop Analysis (GUI)
**Scenario**: You have access to download cluster data and want a visual interface

1. Run data collection command on cluster
2. Download `openshift-data.json` to your laptop
3. Start the web server locally
4. Upload JSON file via browser UI
5. Get interactive analysis with charts

### Use Case 2: Supportshell Analysis (CLI)
**Scenario**: Working in must-gather or supportshell where you can't transfer files

1. Copy `cli-analyzer.py` to supportshell
2. Run YAML data collection command
3. Execute CLI analyzer directly in terminal
4. Get immediate text-based results
5. No file transfer needed!

### Use Case 3: CI/CD Pipeline
**Scenario**: Automated compatibility checking

```bash
# In your pipeline
curl -X POST http://analyzer:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d @openshift-data.json
```

---

## 📖 API Documentation

### POST /api/analyze
Analyze cluster operator compatibility

**Request Body:**
```json
{
  "cluster_data": {...},
  "target_ocp_version": "4.21"
}
```

**Response:**
```json
{
  "analysis_id": "uuid",
  "cluster_info": {...},
  "compatibility_results": [...],
  "risk_score": "high",
  "ai_summary": "..."
}
```

---

## 🛠️ Troubleshooting

### Web UI Issues
- **Port 8000 already in use**: Kill existing process or change port in `simple_server.py`
- **File not uploading**: Check that JSON is valid using `jq`
- **Browser cache**: Hard refresh (Cmd+Shift+R / Ctrl+Shift+F5)

### CLI Issues
- **PyYAML not found**: Install with `pip3 install pyyaml`
- **No color output**: Check terminal supports ANSI colors
- **Permission denied**: Make script executable: `chmod +x cli-analyzer.py`

---

## 📝 License

MIT License

---

## 🙋 Support

For issues or questions:
1. Check the troubleshooting section
2. Review example usage
3. Verify your data format matches the examples

---

## 🎓 Tips

### For Supportshell Users
- The CLI tool is **completely standalone** - just Python + PyYAML
- No need to install the backend server
- Results display immediately in your terminal
- Perfect for environments with no GUI access

### For Desktop Users
- Web UI provides **better visualization** with charts and tables
- Can analyze multiple scenarios quickly
- **Export reports** as HTML/PDF (coming soon)
- Supports both JSON and YAML uploads

### Data Collection Best Practices
- Run collection commands from a cluster admin account
- Ensure you have access to all namespaces (`-A` flag)
- Use `jq` to validate JSON output before uploading
- Keep collected data secure (may contain cluster information)

---

## 🔮 Roadmap

- [ ] PDF report generation
- [ ] More operator support
- [ ] Historical analysis tracking
- [ ] Automated upgrade recommendations
- [ ] Integration with Red Hat APIs
- [ ] Multi-cluster comparison

---

**Happy Upgrading! 🚀**
