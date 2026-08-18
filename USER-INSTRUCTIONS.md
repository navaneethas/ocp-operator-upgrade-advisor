# 📖 How to Use - OpenShift Operator Upgrade Advisor

**Simple instructions for users**

---

## 🎯 What You Need

### Prerequisites
1. ✅ Access to an OpenShift cluster
2. ✅ `oc` CLI installed and logged in
3. ✅ Internet browser (for web UI) OR Python 3.6+ (for CLI)

**That's it!** No special permissions or installations needed.

---

## 📋 Step-by-Step Instructions

### Step 1: Collect Cluster Data (2 minutes)

**Login to your OpenShift cluster:**
```bash
oc login https://api.your-cluster.com:6443
```

**Run this single command to collect all required data:**
```bash
(echo '{"clusterVersion":'; oc get clusterversion version -o json; \
 echo ',"subscriptions":'; oc get sub -A -o json; \
 echo ',"clusterServiceVersions":'; oc get csv -A -o json; \
 echo '}') > cluster-data.json
```

**This creates a file called `cluster-data.json` with all your cluster information.**

---

### Step 2: Analyze (Choose Web UI or CLI)

## 🌐 Option A: Web UI (Easiest)

**1. Open the tool:**
```
https://yourusername.github.io/openshift-upgrade-advisor/
```

**2. Upload your file:**
- Click on the upload box
- Select `cluster-data.json`
- Wait 2 seconds for upload to complete ✅

**3. Select target OpenShift version:**
- Choose from dropdown (4.12 to 4.22)
- Example: If upgrading to 4.22, select "4.22"

**4. Click "Analyze Compatibility"**

**5. Review results! 🎉**

---

## 💻 Option B: CLI (For Advanced Users)

**1. Download the CLI tool:**
```bash
curl -O https://raw.githubusercontent.com/yourusername/openshift-upgrade-advisor/main/cli-analyzer-enhanced.py
```

**2. Run the analysis:**
```bash
python3 cli-analyzer-enhanced.py cluster-data.json --target-ocp 4.22
```

**3. Review results in terminal! 🎉**

---

## 📊 Understanding the Results

### Status Types

| Status | What It Means | What To Do |
|--------|--------------|-----------|
| ✅ **COMPATIBLE** | Operator works with target OCP | Nothing! You're good to go |
| ⚠️ **UPGRADE REQUIRED** | Operator needs upgrade first | Upgrade to recommended version |
| ❌ **INCOMPATIBLE** | Operator not available in target | Contact Red Hat support |
| ℹ️ **NON-RED HAT** | Community/certified operator | Check vendor documentation |
| ❓ **UNKNOWN** | No data available | Check Red Hat docs manually |

### Key Information Displayed

**For each operator you'll see:**

1. **Current Version** - What's running now
   ```
   Current Version: 2.4.0+0.1785427615
   ```

2. **Status** - Compatibility with target OCP
   ```
   Status: ⚠ Upgrade Required
   ```

3. **Max Supported OCP** - Highest OCP your current version supports
   ```
   Max Supported OCP: 4.20
   ```

4. **Recommended Version** - Best version for target OCP
   ```
   Recommended: 2.7.0
   ```

5. **Available Versions** - All versions in target catalog
   ```
   Available in 4.22: 2.6.0, 2.7.0
   ```

6. **Explanation** - What you need to do
   ```
   Explanation: ansible-automation-platform-operator v2.4.0 
   is only supported up to OCP 4.20. Target OCP 4.22 requires 
   upgrade to v2.7.0.
   ```

---

## 📝 Example Scenario

### You want to upgrade from OCP 4.14 → 4.22

**Step 1: Collect data**
```bash
oc login
(echo '{"clusterVersion":'; oc get clusterversion version -o json; \
 echo ',"subscriptions":'; oc get sub -A -o json; \
 echo ',"clusterServiceVersions":'; oc get csv -A -o json; \
 echo '}') > cluster-data.json
```

**Step 2: Upload to tool**
- Go to web UI
- Upload `cluster-data.json`
- Select "4.22" as target

**Step 3: Results show:**
```
Summary:
- Total Operators: 10
- ✅ Compatible: 5
- ⚠️ Upgrade Required: 3
- ❌ Incompatible: 2

Details:
[1] openshift-gitops-operator
    Current: 1.8.6
    Status: ✅ COMPATIBLE
    Max OCP: 4.22
    → No action needed!

[2] advanced-cluster-management
    Current: 2.9.9
    Status: ⚠ UPGRADE REQUIRED
    Max OCP: 4.15
    Recommended: 2.17.0
    → Upgrade ACM to 2.17.0 before OCP upgrade

[3] custom-operator
    Status: ℹ️ NON-RED HAT OPERATOR
    → Check with operator vendor
```

**Step 4: Take action**
- Upgrade ACM: `oc patch subscription acm-subscription...`
- Leave GitOps alone (already compatible)
- Check vendor docs for custom operator

**Step 5: Upgrade OCP to 4.22** ✅

---

## 🔒 Privacy & Security

### What data is collected?
**NONE!** Your cluster data:
- ❌ Never leaves your environment (web UI processes locally)
- ❌ Not sent to any external server
- ❌ Not stored anywhere
- ❌ Not logged

### Is it safe?
**YES!** The tool is:
- ✅ Read-only (never modifies your cluster)
- ✅ Open source (audit the code)
- ✅ No external dependencies
- ✅ No authentication required

---

## ❓ FAQ

### Q: Do I need cluster-admin permissions?
**A:** No! Any user who can run `oc get` commands can use this tool.

### Q: What if I don't have `oc` CLI?
**A:** You need `oc` to collect data. Download from: https://mirror.openshift.com/pub/openshift-v4/clients/ocp/

### Q: Can I analyze multiple clusters?
**A:** Yes! Just collect data from each cluster separately and analyze one at a time.

### Q: Does this work for disconnected/air-gapped clusters?
**A:** Yes! Collect the data, transfer `cluster-data.json` to a connected machine, then analyze.

### Q: How often should I run this?
**A:** Before every OpenShift upgrade to check operator compatibility.

### Q: What if my operator shows "UNKNOWN"?
**A:** It might be a community/certified operator, or newer than our database. Check Red Hat documentation manually.

### Q: Can I save/download the results?
**A:** Yes! (Coming soon: HTML/PDF export feature)

### Q: Does this modify my cluster?
**A:** NO! It's completely read-only. It only analyzes data.

---

## 🆘 Troubleshooting

### Issue: "oc command not found"
**Solution:** Install OpenShift CLI from https://mirror.openshift.com/pub/openshift-v4/clients/ocp/

### Issue: "Unable to connect to cluster"
**Solution:** Login first: `oc login https://api.your-cluster.com:6443`

### Issue: File upload shows error
**Solution:** 
1. Check file is valid JSON
2. Make sure all 3 sections are included (clusterVersion, subscriptions, csvs)
3. Try CLI version instead

### Issue: Results show all operators as "UNKNOWN"
**Solution:** 
1. Check compatibility_matrix.json is loaded (should show "180 operators")
2. Verify operator names match Red Hat operators

### Issue: Backend server won't start
**Solution:**
```bash
# Check Python version
python3 --version  # Need 3.6+

# Try running directly
cd backend
python3 simple_server_enhanced.py
```

---

## 💡 Tips

1. **Before Upgrades:** Always run this tool BEFORE planning OCP upgrades
2. **Planning:** Use results to schedule operator upgrades first
3. **Testing:** Test operator upgrades in dev/staging before production
4. **Documentation:** Take screenshots of results for your upgrade records
5. **Multiple Jumps:** If jumping multiple versions (4.14→4.22), check each intermediate version

---

## 📞 Need Help?

- 🐛 **Bug reports:** [GitHub Issues](https://github.com/yourusername/openshift-upgrade-advisor/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/yourusername/openshift-upgrade-advisor/discussions)
- 📧 **Email:** your.email@company.com

---

## ✅ Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│  OpenShift Operator Upgrade Advisor            │
│  Quick Reference                                │
├─────────────────────────────────────────────────┤
│                                                 │
│  1️⃣  Collect Data:                              │
│     oc login                                    │
│     (echo '{"clusterVersion":'; \               │
│      oc get clusterversion version -o json; \   │
│      echo ',"subscriptions":'; \                │
│      oc get sub -A -o json; \                   │
│      echo ',"clusterServiceVersions":'; \       │
│      oc get csv -A -o json; \                   │
│      echo '}') > cluster-data.json              │
│                                                 │
│  2️⃣  Analyze:                                    │
│     Web: Upload to tool                         │
│     CLI: python3 cli-analyzer.py \              │
│          cluster-data.json --target-ocp 4.22    │
│                                                 │
│  3️⃣  Review Results:                             │
│     ✅ Compatible → No action                    │
│     ⚠️  Upgrade Required → Upgrade first         │
│     ❌ Incompatible → Check with Red Hat        │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

**That's it! Simple and easy.** 🎉

**Questions? Just ask!**
