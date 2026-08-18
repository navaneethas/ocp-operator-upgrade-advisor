# 🚀 OpenShift Operator Upgrade Advisor

**Check operator compatibility before upgrading OpenShift clusters**

I built this tool to help us (and customers) check if their operators are compatible with target OpenShift versions. I noticed many struggle with manual version checking, so this should make it much easier.

Give it a spin and let me know what you think! (created by Claude) 🤖

---

## 🎯 What It Does

Before upgrading your OpenShift cluster, this tool tells you:

- ✅ Which operators are compatible with the target OCP version
- ⚠️ Which operators need upgrades
- ❌ Which operators won't work
- 📊 Recommended versions for each operator
- 🎯 Maximum OCP version each operator supports

**Coverage:** 180 Red Hat operators across OCP 4.12 → 4.22

---

## 🌐 Try It Now

### Live Demo
**Web UI:** https://yourusername.github.io/openshift-upgrade-advisor/

### Quick Start

**1. Collect your cluster data:**
```bash
(echo '{"clusterVersion":'; oc get clusterversion version -o json; \
 echo ',"subscriptions":'; oc get sub -A -o json; \
 echo ',"clusterServiceVersions":'; oc get csv -A -o json; \
 echo '}') > cluster-data.json
```

**2. Upload & analyze:**
- Open the web UI
- Upload `cluster-data.json`
- Select target OCP version
- Click "Analyze Compatibility"

**3. Review results!**

---

## 🖥️ CLI Version

For those who prefer command-line:

```bash
# Download
curl -O https://raw.githubusercontent.com/yourusername/openshift-upgrade-advisor/main/cli-analyzer-enhanced.py

# Run
python3 cli-analyzer-enhanced.py cluster-data.json --target-ocp 4.22
```

---

## 🐳 Self-Host (Optional)

Want to run it on your own infrastructure?

### Docker
```bash
docker run -d -p 8000:8000 ghcr.io/yourusername/ocp-upgrade-advisor:latest
```

### Docker Compose
```bash
git clone https://github.com/yourusername/openshift-upgrade-advisor.git
cd openshift-upgrade-advisor
docker-compose up -d
```

### Manual
```bash
git clone https://github.com/yourusername/openshift-upgrade-advisor.git
cd openshift-upgrade-advisor/backend
python3 simple_server_enhanced.py
```

Access at: http://localhost:8000

---

## ✨ Features

- ✅ **180 Red Hat Operators** - Complete coverage
- ✅ **OCP 4.12 - 4.22** - All recent versions
- ✅ **Web GUI + CLI** - Use what you prefer
- ✅ **No External Dependencies** - Python stdlib only
- ✅ **Color-Coded Results** - Easy to understand
- ✅ **Version Recommendations** - Know what to upgrade to
- ✅ **Build Metadata Handling** - Works with versions like `2.4.0+0.12345`
- ✅ **Catalog Validation** - Detects non-Red Hat operators
- ✅ **Offline Capable** - No internet required for analysis

---

## 📸 Screenshots

### CLI Output
```
[1] ansible-automation-platform-operator
  Current Version:    2.4.0+0.1785427615
  Status:             ⚠ Incompatible Upgrade Required
  Max Supported OCP:  4.20
  Recommended:        2.7.0
  Available in 4.22:  2.6.0, 2.7.0
  
  Explanation: ansible-automation-platform-operator v2.4.0+0.1785427615 
  is only supported up to OCP 4.20. Target OCP 4.22 requires upgrade to v2.7.0.
```

---

## 🎓 How It Works

1. **Data Collection:** Gather cluster data using `oc` commands
2. **Version Extraction:** Parse operator versions from CSVs
3. **Compatibility Check:** Match against Red Hat operator catalogs (4.12-4.22)
4. **Analysis:** Determine compatibility status and recommendations
5. **Display:** Show results in web UI or CLI

**Data Source:** Red Hat operator catalog indexes collected via `oc-mirror`

---

## 🤝 Contributing

Found a bug or have a suggestion? Please open an issue!

---

## 🔒 Privacy & Security

- ✅ **No data collection** - Your cluster data never leaves your environment
- ✅ **No external API calls** - Fully self-contained
- ✅ **Read-only** - Never modifies your cluster
- ✅ **No authentication required** - Simple to use
- ✅ **Open source** - Audit the code yourself

---

## 📋 Supported Operators

180 Red Hat operators including:
- Advanced Cluster Management (ACM)
- OpenShift GitOps (ArgoCD)
- OpenShift Pipelines (Tekton)
- Cluster Logging
- Service Mesh (Istio)
- Serverless (Knative)
- Ansible Automation Platform
- And 170+ more!

---

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT-GUIDE.md) - How to deploy on your infrastructure
- [Team README](TEAM-README.md) - User guide for your team
- [GitHub Pages Setup](github-pages-setup.md) - Deploy to GitHub Pages

---

## 🙏 Credits

Created by [Your Name] with assistance from Claude (Anthropic)

---

## 📜 License

MIT License

---

## 💬 Feedback

Give it a spin and let me know what you think!

**Built with ❤️ to make OpenShift upgrades easier**
