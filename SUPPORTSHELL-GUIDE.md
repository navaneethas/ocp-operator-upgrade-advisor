# Supportshell Quick Guide (No Installation Required!)

## 🎯 Problem Solved
You're in a supportshell environment where you:
- ❌ Cannot install packages (no pip/yum)
- ❌ Cannot transfer files (no scp/sftp)
- ❌ Cannot access external networks
- ✅ **BUT you CAN copy-paste text!**

## 📋 Solution: Copy-Paste Method

### Step 1: Collect Cluster Data in Supportshell

Run this command in your supportshell to create the JSON file:

```bash
(echo '{"cluster_data":'; \
 echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; \
 echo '  "subscriptions":'; oc get sub -A -o json; echo ','; \
 echo '  "clusterServiceVersions":'; oc get csv -A -o json; echo ','; \
 echo '  "catalogSources":'; oc get catalogsource -A -o json; echo ','; \
 echo '  "packageManifests":'; oc get packagemanifest -o json; \
 echo '}') > openshift-data.json
```

This creates `openshift-data.json` with all required information.

---

### Step 2: Create the Analyzer Script (Copy-Paste)

**Method 1: Direct Copy-Paste**

In your supportshell, create the script:

```bash
cat > analyzer.py << 'SCRIPT_END'
```

Then **copy the ENTIRE contents** of `cli-analyzer-standalone.py` and paste into your terminal.

Then type:
```bash
SCRIPT_END
```

**Method 2: Using vi/vim**

```bash
vi analyzer.py
```

- Press `i` to enter insert mode
- Copy and paste the entire script
- Press `ESC`
- Type `:wq` and press Enter

---

### Step 3: Run the Analysis

```bash
python3 analyzer.py openshift-data.json --target-ocp 4.21
```

Or interactively (it will prompt for target version):
```bash
python3 analyzer.py openshift-data.json
```

---

## 🚀 Complete Copy-Paste Workflow

Here's the **complete workflow** you can copy-paste section by section:

### 1️⃣ Collect Data
```bash
(echo '{"cluster_data":'; \
 echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; \
 echo '  "subscriptions":'; oc get sub -A -o json; echo ','; \
 echo '  "clusterServiceVersions":'; oc get csv -A -o json; echo ','; \
 echo '  "catalogSources":'; oc get catalogsource -A -o json; echo ','; \
 echo '  "packageManifests":'; oc get packagemanifest -o json; \
 echo '}') > openshift-data.json
```

### 2️⃣ Create Script (Start Heredoc)
```bash
cat > analyzer.py << 'SCRIPT_END'
#!/usr/bin/env python3
```

### 3️⃣ Copy-Paste Script Content
👉 **Copy the ENTIRE content of `cli-analyzer-standalone.py`** from line 1 to the end and paste it here

### 4️⃣ Close Heredoc
```bash
SCRIPT_END
```

### 5️⃣ Make Executable (Optional)
```bash
chmod +x analyzer.py
```

### 6️⃣ Run Analysis
```bash
python3 analyzer.py openshift-data.json --target-ocp 4.21
```

---

## 🎨 Expected Output

You'll see colorful, formatted output like:

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
  Max Supported OCP:  4.21
  Supported Versions: 1.18, 1.19, 1.20, 1.21
  Risk Level:         LOW
  Explanation: openshift-gitops-operator version 1.18.2 is compatible...

...
```

---

## ✅ Why This Works

- **Zero Dependencies**: Uses only Python standard library (json, sys, argparse)
- **No PyYAML**: Works with JSON format only (always available in Python)
- **No Installation**: Pure copy-paste, no pip/yum needed
- **No Network**: Script is self-contained
- **No File Transfer**: Just copy-paste the script text

---

## 🔧 Troubleshooting

### "python3: command not found"
Try `python` instead:
```bash
python analyzer.py openshift-data.json --target-ocp 4.21
```

### Script paste failed
Use the `vi` method instead:
```bash
vi analyzer.py
# Press 'i', paste content, ESC, ':wq'
```

### JSON syntax error
Validate your JSON:
```bash
python3 -m json.tool openshift-data.json > /dev/null
```

---

## 📝 Quick Reference Card

| Step | Command |
|------|---------|
| Collect data | `(echo '{"cluster_data":'; echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; echo '  "subscriptions":'; oc get sub -A -o json; echo ','; echo '  "clusterServiceVersions":'; oc get csv -A -o json; echo ','; echo '  "catalogSources":'; oc get catalogsource -A -o json; echo ','; echo '  "packageManifests":'; oc get packagemanifest -o json; echo '}') > openshift-data.json` |
| Create script | `cat > analyzer.py << 'SCRIPT_END'` |
| Paste script | Copy-paste `cli-analyzer-standalone.py` content |
| Close script | Type `SCRIPT_END` and Enter |
| Run analysis | `python3 analyzer.py openshift-data.json --target-ocp 4.21` |

---

## 🎯 Pro Tips

1. **Check Python version** before starting:
   ```bash
   python3 --version
   # Should be 3.6+
   ```

2. **Verify data collected**:
   ```bash
   ls -lh openshift-data.json
   # Should see file size > 0
   ```

3. **Quick test** of script:
   ```bash
   python3 analyzer.py --help
   # Should show help message
   ```

4. **Save output** to file:
   ```bash
   python3 analyzer.py openshift-data.json --target-ocp 4.21 > analysis-report.txt
   ```

---

**That's it! No installation, no file transfer, just copy-paste and run!** 🚀
