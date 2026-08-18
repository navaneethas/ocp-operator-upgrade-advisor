# Quick Start Guide

## 🎯 Two Ways to Use This Tool

### Option 1: Web UI (JSON) - For Desktop/Laptop Analysis
**Best for**: When you can download files and have browser access

```bash
# On OpenShift cluster - collect data as JSON
(echo '{"cluster_data":'; \
 echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; \
 echo '  "subscriptions":'; oc get sub -A -o json; echo ','; \
 echo '  "clusterServiceVersions":'; oc get csv -A -o json; echo ','; \
 echo '  "catalogSources":'; oc get catalogsource -A -o json; echo ','; \
 echo '  "packageManifests":'; oc get packagemanifest -o json; \
 echo '}') | jq > openshift-data.json

# On your laptop - start server and analyze
cd backend
python3 simple_server.py
# Then open http://localhost:8000 and upload the JSON file
```

---

### Option 2: CLI (YAML) - For Supportshell/Must-Gather
**Best for**: When working in supportshell, must-gather, or restricted environments

```bash
# Step 1: Collect data as YAML (in supportshell)
(echo 'cluster_data:'; \
 echo '  clusterVersion:'; oc get clusterversion version -o yaml | sed 's/^/    /'; \
 echo '  subscriptions:'; oc get sub -A -o yaml | sed 's/^/    /'; \
 echo '  clusterServiceVersions:'; oc get csv -A -o yaml | sed 's/^/    /'; \
 echo '  catalogSources:'; oc get catalogsource -A -o yaml | sed 's/^/    /'; \
 echo '  packageManifests:'; oc get packagemanifest -o yaml | sed 's/^/    /') > openshift-data.yaml

# Step 2: Copy CLI analyzer to supportshell
# (Copy cli-analyzer.py to the same location)

# Step 3: Run analysis directly in terminal
python3 cli-analyzer.py openshift-data.yaml --target-ocp 4.21
```

---

## 📦 What You Need

### For Web UI:
- `backend/simple_server.py` (server)
- `index.html` (UI)
- Python 3.7+
- PyYAML (`pip3 install pyyaml`)

### For CLI:
- `cli-analyzer.py` (standalone script)
- Python 3.7+
- PyYAML (`pip3 install pyyaml`)

---

## 🎨 CLI Output Preview

```
================================================================================
              OpenShift Operator Upgrade Advisor - Analysis Report              
================================================================================

Cluster Information:
  Current Version:  4.19.8
  Target Version:   4.21
  Total Operators:  1

Compatibility Summary:
  ✓ Compatible:          0
  ⚠ Upgrade Required:    1
  ✗ Incompatible:        1

Risk Assessment:
  🔴 CRITICAL: 1 incompatible operators found.

────────────────────────────────────────────────────────────────────────────────
Detailed Operator Analysis
────────────────────────────────────────────────────────────────────────────────

[1] advanced-cluster-management
  Current Version:    2.13.9
  Status:             ⚠ Incompatible Upgrade Required
  Max Supported OCP:  4.19
  Recommended:        2.17
  Supported Versions: 2.15, 2.16, 2.17
  Risk Level:         HIGH
  Explanation: advanced-cluster-management version 2.13.9 is incompatible...
```

---

## ✅ Quick Checklist

### Before Running:
- [ ] Have cluster-admin access to OpenShift
- [ ] Python 3.7+ installed
- [ ] PyYAML installed (`pip3 install pyyaml`)
- [ ] Know your target OpenShift version

### For GUI Users:
- [ ] Can download files from cluster
- [ ] Have browser access
- [ ] Port 8000 available

### For CLI Users:
- [ ] Working in supportshell/must-gather
- [ ] Can run Python scripts
- [ ] Need results in terminal

---

**That's it! Pick your method and start analyzing!** 🚀
