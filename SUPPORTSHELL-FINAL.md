# Supportshell Solution - FINAL ANSWER

## ✅ The Problem
You're in a supportshell where:
- ❌ Cannot install packages (no pip)
- ❌ Cannot transfer files (no scp)  
- ⚠️  `oc get -o json` might still output YAML

## ✅ The Solution

Use **`cli-analyzer-universal.py`** - it handles BOTH JSON and YAML with **zero dependencies**!

---

## 🚀 Complete Workflow

### Step 1: Collect Data (Copy-Paste This Command)

**Option A: If `-o json` works (outputs actual JSON):**
```bash
(echo '{"cluster_data":'; \
 echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; \
 echo '  "subscriptions":'; oc get sub -A -o json; echo ','; \
 echo '  "clusterServiceVersions":'; oc get csv -A -o json; echo ','; \
 echo '  "catalogSources":'; oc get catalogsource -A -o json; echo ','; \
 echo '  "packageManifests":'; oc get packagemanifest -o json; \
 echo '}') > openshift-data.json
```

**Option B: If it outputs YAML (or you're unsure):**
```bash
(echo 'cluster_data:'; \
 echo '  clusterVersion:'; oc get clusterversion version -o yaml | sed 's/^/    /'; \
 echo '  subscriptions:'; oc get sub -A -o yaml | sed 's/^/    /'; \
 echo '  clusterServiceVersions:'; oc get csv -A -o yaml | sed 's/^/    /'; \
 echo '  catalogSources:'; oc get catalogsource -A -o yaml | sed 's/^/    /'; \
 echo '  packageManifests:'; oc get packagemanifest -o yaml | sed 's/^/    /') > openshift-data.yaml
```

**Not sure which format you have?** Run this to check:
```bash
oc get clusterversion version -o json | head -1
# If you see "{" = JSON
# If you see "---" or "apiVersion:" = YAML
```

---

### Step 2: Create the Analyzer Script

**Method 1: Using heredoc (Recommended)**

```bash
cat > analyzer.py << 'SCRIPT_END'
```

👉 **Now copy the ENTIRE content of `cli-analyzer-universal.py` and paste it**

```bash
SCRIPT_END
```

**Method 2: Using vi/vim**

```bash
vi analyzer.py
```
- Press `i` to enter insert mode
- Paste the entire script content
- Press `ESC`
- Type `:wq` and press ENTER

---

### Step 3: Run the Analysis

**For JSON file:**
```bash
python3 analyzer.py openshift-data.json --target-ocp 4.21
```

**For YAML file:**
```bash
python3 analyzer.py openshift-data.yaml --target-ocp 4.21
```

**Or run interactively (will prompt for target version):**
```bash
python3 analyzer.py openshift-data.json
```

---

## 📋 Quick Test

After creating the script, test it works:

```bash
# Test script is valid Python
python3 -c "import analyzer" 2>/dev/null && echo "✓ Script OK" || echo "✗ Script has errors"

# Test help message
python3 analyzer.py --help
```

---

## 🎨 What You'll See

Color-coded terminal output:

```
================================================================================
              OpenShift Operator Upgrade Advisor - Analysis Report              
================================================================================

Cluster Information:
  Current Version:  4.19.8
  Target Version:   4.21
  Total Operators:  5

Compatibility Summary:
  ✓ Compatible:          3
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

[2] openshift-gitops-operator
  Current Version:    1.18.2
  Status:             ✓ Compatible
  ...
```

---

## ✅ Why This Works

### Zero Dependencies
Uses **ONLY** Python standard library:
- `json` - Parse JSON (built-in)
- `sys` - System functions (built-in)
- `argparse` - CLI arguments (built-in)
- `datetime` - Timestamps (built-in)
- `re` - Regular expressions (built-in)

### Automatic Format Detection
- Tries JSON first (fast, standard)
- Falls back to simple YAML parser if JSON fails
- **No PyYAML required!**

### Works Anywhere
- Any Python 3.6+ environment
- No network access needed
- No file transfers needed
- Just copy-paste!

---

## 🔧 Troubleshooting

### "python3: command not found"
Try `python` instead:
```bash
python analyzer.py openshift-data.json --target-ocp 4.21
```

### "No such file or directory"
Make sure you created the data file:
```bash
ls -lh openshift-data.*
# Should show file with size > 0
```

### "Could not parse file"
Check your data file format:
```bash
head -5 openshift-data.json
# Should show valid JSON or YAML
```

### Script paste failed
- Make sure you pasted the ENTIRE script (all ~700 lines)
- Try using `vi` method instead of heredoc
- Check for copy-paste errors

---

## 💡 Pro Tips

### Save Output to File
```bash
python3 analyzer.py openshift-data.json --target-ocp 4.21 > analysis-report.txt
```

### Check Python Version
```bash
python3 --version
# Should be 3.6 or higher
```

### Verify Data Collected
```bash
wc -l openshift-data.json
# Should show many lines (not empty)

head -20 openshift-data.json
# Should show cluster data
```

### Multiple Target Versions
```bash
# Test different upgrade paths
python3 analyzer.py openshift-data.json --target-ocp 4.19
python3 analyzer.py openshift-data.json --target-ocp 4.20
python3 analyzer.py openshift-data.json --target-ocp 4.21
```

---

## 🎯 The Magic

This script:
- ✅ **Auto-detects** JSON vs YAML format
- ✅ **Zero installations** - pure Python stdlib
- ✅ **Works everywhere** Python 3.6+ exists
- ✅ **No file transfer** - just copy-paste
- ✅ **Same analysis** as the GUI version
- ✅ **Color output** for readability

**Perfect for supportshell environments!** 🚀

---

## 📝 Quick Reference Card

| Step | Command |
|------|---------|
| **Check format** | `oc get clusterversion version -o json \| head -1` |
| **Collect JSON** | `(echo '{"cluster_data":'; echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; echo '  "subscriptions":'; oc get sub -A -o json; echo ','; echo '  "clusterServiceVersions":'; oc get csv -A -o json; echo ','; echo '  "catalogSources":'; oc get catalogsource -A -o json; echo ','; echo '  "packageManifests":'; oc get packagemanifest -o json; echo '}') > openshift-data.json` |
| **Collect YAML** | `(echo 'cluster_data:'; echo '  clusterVersion:'; oc get clusterversion version -o yaml \| sed 's/^/    /'; echo '  subscriptions:'; oc get sub -A -o yaml \| sed 's/^/    /'; echo '  clusterServiceVersions:'; oc get csv -A -o yaml \| sed 's/^/    /'; echo '  catalogSources:'; oc get catalogsource -A -o yaml \| sed 's/^/    /'; echo '  packageManifests:'; oc get packagemanifest -o yaml \| sed 's/^/    /') > openshift-data.yaml` |
| **Create script** | `cat > analyzer.py << 'SCRIPT_END'` (then paste, then type `SCRIPT_END`) |
| **Run analysis** | `python3 analyzer.py openshift-data.json --target-ocp 4.21` |
| **Save output** | `python3 analyzer.py openshift-data.json --target-ocp 4.21 > report.txt` |

---

**You're all set! No installations. No file transfers. Just copy-paste and analyze!** ✨
