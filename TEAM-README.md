# 🚀 OpenShift Operator Upgrade Advisor

**Check operator compatibility before upgrading OpenShift clusters**

---

## 🎯 What Does It Do?

Before upgrading your OpenShift cluster from **4.X** to **4.Y**, this tool tells you:

✅ Which operators are compatible  
⚠️ Which operators need upgrades  
❌ Which operators won't work  
📊 Recommended versions for each operator  

**Covers:** 180 Red Hat operators across OCP 4.12 → 4.22

---

## 🌐 Access the Tool

**Web UI:** http://your-server:8000  
**CLI:** `python3 cli-analyzer-enhanced.py cluster-data.json --target-ocp 4.22`

---

## 📋 How to Use

### Step 1: Collect Cluster Data

Run this command on your OpenShift cluster:

```bash
(echo '{"clusterVersion":'; oc get clusterversion version -o json; \
 echo ',"subscriptions":'; oc get sub -A -o json; \
 echo ',"clusterServiceVersions":'; oc get csv -A -o json; \
 echo '}') > cluster-data.json
```

### Step 2: Analyze

**Option A: Web UI**
1. Open http://your-server:8000
2. Upload `cluster-data.json`
3. Select target OCP version (e.g., 4.22)
4. Click "Analyze Compatibility"
5. Review results!

**Option B: CLI**
```bash
python3 cli-analyzer-enhanced.py cluster-data.json --target-ocp 4.22
```

### Step 3: Read Results

**Example Output:**

```
✅ openshift-gitops-operator v1.10.6
   Status: Compatible with OCP 4.22
   Max OCP: 4.22
   
⚠️ advanced-cluster-management v2.9.9
   Status: Upgrade Required
   Max OCP: 4.15
   Recommended: v2.17.0 for OCP 4.22
```

---

## 🎨 Features

- ✅ **180 Red Hat Operators** - Complete coverage
- ✅ **OCP 4.12 - 4.22** - All recent versions
- ✅ **Web GUI + CLI** - Use what you prefer
- ✅ **Color-Coded Status** - Easy to understand
- ✅ **Version Recommendations** - Know what to upgrade to
- ✅ **Max OCP Detection** - See highest supported version
- ✅ **Catalog Validation** - Only checks Red Hat operators
- ✅ **No External Dependencies** - Python stdlib only

---

## ❓ FAQ

### Q: What clusters can I analyze?
**A:** Any OpenShift 4.x cluster with operators installed.

### Q: Does it work for community/certified operators?
**A:** No, it's designed for **Red Hat operators only**. Community and certified operators will show a clear message to check their documentation.

### Q: Can I analyze without uploading to a server?
**A:** Yes! Use the **CLI version** - completely offline, no upload needed.

### Q: How often is the compatibility data updated?
**A:** The data is from Red Hat's operator catalogs. Updates can be done monthly or before major upgrades.

### Q: Does it modify my cluster?
**A:** No! It's **read-only**. It only analyzes data, never changes anything.

### Q: What if my operator version has build metadata (e.g., `2.4.0+0.12345`)?
**A:** ✅ We handle that! Version normalization strips build metadata automatically.

---

## 📖 Supported Operators (Examples)

- Advanced Cluster Management (ACM)
- OpenShift GitOps (ArgoCD)
- OpenShift Pipelines (Tekton)
- Cluster Logging
- Elasticsearch
- Service Mesh (Istio)
- Serverless (Knative)
- And 170+ more!

---

## 🔒 Security & Privacy

- ✅ **No data leaves your network** - Runs on your infrastructure
- ✅ **No external API calls** - Fully self-contained
- ✅ **No authentication required** - Simple access
- ✅ **Read-only analysis** - Never modifies clusters
- ✅ **No data storage** - Analysis is temporary

---

## 💡 Tips

1. **Before Upgrades:** Always run this before planning OCP upgrades
2. **Planning:** Use results to schedule operator upgrades first
3. **Documentation:** Download HTML report for records
4. **Testing:** Test operator upgrades in dev/staging first
5. **Batch Analysis:** Can analyze multiple clusters and compare

---

## 📞 Support

**Issues?** Contact: [your-team-contact]  
**Updates?** Check: [your-deployment-location]  
**Documentation:** See DEPLOYMENT-GUIDE.md

---

## 🎯 Quick Reference

| Current OCP | Target OCP | Action |
|-------------|------------|--------|
| 4.14 | 4.15 | ✅ Minor jump - Low risk |
| 4.14 | 4.16 | ⚠️ Two versions - Medium risk |
| 4.14 | 4.22 | ❌ Four versions - Plan carefully! |

**Best Practice:** Upgrade one minor version at a time (4.14 → 4.15 → 4.16)

---

## 📊 Understanding Results

### Status Badges

| Badge | Meaning | Action |
|-------|---------|--------|
| ✅ **COMPATIBLE** | Current version works with target OCP | No action needed |
| ⚠️ **UPGRADE REQUIRED** | Must upgrade operator first | Upgrade to recommended version |
| ❌ **INCOMPATIBLE** | Not available in target OCP | Contact Red Hat support |
| ℹ️ **NON-RED HAT** | Community/certified operator | Check vendor documentation |
| ❓ **UNKNOWN** | No data available | Check Red Hat documentation |

### Fields Explained

- **Current Version:** What's running now
- **Max Supported OCP:** Highest OCP version that supports current operator version
- **Recommended Version:** Best version for target OCP
- **Available in X.XX:** All versions available in target catalog

---

## 🚀 Example Workflow

### Scenario: Upgrade OCP 4.14 → 4.16

1. **Collect data** from production cluster
2. **Run analysis** with target OCP 4.16
3. **Review results:**
   - 8 operators ✅ Compatible
   - 3 operators ⚠️ Need upgrades
   - 0 operators ❌ Incompatible
4. **Plan upgrades:**
   - ACM: 2.9.9 → 2.14.3
   - GitOps: 1.8.6 → 1.19.5
   - Logging: 5.8.22 → 6.1.9
5. **Execute in dev/test** environment
6. **Verify** everything works
7. **Proceed** with OCP upgrade!

---

## ✅ Benefits

- 🎯 **Prevent failed upgrades** - Know issues before upgrading
- ⏱️ **Save time** - No manual version checking
- 📊 **Better planning** - Clear upgrade path
- 🔍 **Complete coverage** - All 180 Red Hat operators
- 💰 **Cost savings** - Avoid downtime from incompatible operators

---

**Ready to analyze?** → http://your-server:8000 🚀
