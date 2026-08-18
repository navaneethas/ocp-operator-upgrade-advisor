# 🚀 How to Use in Supportshell - Geminicli Skill

**For Red Hat Support Engineers using supportshell with geminicli**

---

## 📋 Prerequisites

- Access to supportshell
- Geminicli installed (already available in supportshell)
- Customer must-gather or access to OpenShift cluster

---

## ⚡ Quick Start (3 Steps)

### Step 1: Download the Skill File

In supportshell, download the geminicli skill:

```bash
curl -o ocp-operator-compatibility.md https://raw.githubusercontent.com/navaneethas/ocp-operator-upgrade-advisor/main/ocp-operator-compatibility.md
```

### Step 2: Download the Compatibility Matrix

```bash
curl -o compatibility_matrix.json https://raw.githubusercontent.com/navaneethas/ocp-operator-upgrade-advisor/main/compatibility_matrix.json
```

**File size:** 103 KB (should download in <5 seconds)

### Step 3: Use Geminicli to Analyze

```bash
# Navigate to the must-gather directory
cd /path/to/must-gather

# Run geminicli with the skill
geminicli analyze operator compatibility for OCP 4.22
```

Geminicli will:
- ✅ Automatically read the skill file
- ✅ Extract cluster data from must-gather
- ✅ Load the compatibility matrix
- ✅ Analyze operator compatibility
- ✅ Show results with recommendations

---

## 📝 What the Skill Does

When you run geminicli with operator-related questions, it will:

1. **Extract Data from Must-Gather**
   - ClusterVersion (current OCP)
   - Subscriptions (installed operators)
   - ClusterServiceVersions (operator versions)

2. **Check Compatibility**
   - Compare against target OCP version
   - Identify incompatible operators
   - Find recommended versions
   - Detect non-Red Hat operators

3. **Generate Report**
   - Color-coded status for each operator
   - Max supported OCP version
   - Recommended upgrade versions
   - Available versions in target OCP
   - Clear explanations

---

## 💬 Example Geminicli Commands

```bash
# Basic analysis
geminicli check operator compatibility for OCP 4.20

# With specific target version
geminicli analyze operators for upgrade to 4.22

# Check specific operator
geminicli is ACM compatible with OCP 4.21?

# List all incompatible operators
geminicli which operators need upgrades for 4.20?
```

---

## 📊 Sample Output

```
================================================================================
          OpenShift Operator Compatibility Report          
================================================================================

Cluster Information:
  Current OCP:  4.18.0
  Target OCP:   4.20
  Total Operators: 9

Summary:
  ✓ Compatible: 2
  ⚠ Upgrade Required: 5
  ✗ Incompatible: 2

────────────────────────────────────────────────────────────────────────────────

[1] advanced-cluster-management
  Current Version: 2.9.9
  Status: ⚠ Upgrade Required
  Max OCP: 4.15
  Recommended: 2.13.10
  Available in 4.20: 2.11.3, 2.12.5, 2.13.10
  → Upgrade to v2.13.10 for OCP 4.20 support

[2] cluster-logging
  Current Version: 6.3.4
  Status: ✓ Compatible
  Max OCP: 4.20
  → Already compatible with OCP 4.20
```

---

## 🔧 Manual Method (If Geminicli Doesn't Work)

If geminicli has issues, you can run the Python script directly:

### 1. Download the CLI Analyzer
```bash
curl -o check-compatibility.py https://raw.githubusercontent.com/navaneethas/ocp-operator-upgrade-advisor/main/cli-analyzer-enhanced.py
```

### 2. Collect Data from Must-Gather
```bash
cd /path/to/must-gather

(echo '{"clusterVersion":'; cat */cluster-scoped-resources/config.openshift.io/clusterversions/version.yaml | python3 -c "import yaml, json, sys; print(json.dumps(yaml.safe_load(sys.stdin)))"; \
 echo ',"subscriptions":'; find . -path "*/operators.coreos.com/subscriptions/*.yaml" -exec cat {} \; | python3 -c "import yaml, json, sys; docs=[d for d in yaml.safe_load_all(sys.stdin) if d]; print(json.dumps({'items': docs}))"; \
 echo ',"clusterServiceVersions":'; find . -path "*/operators.coreos.com/clusterserviceversions/*.yaml" -exec cat {} \; | python3 -c "import yaml, json, sys; docs=[d for d in yaml.safe_load_all(sys.stdin) if d]; print(json.dumps({'items': docs}))"; \
 echo '}') > cluster-data.json
```

### 3. Run the Analyzer
```bash
python3 check-compatibility.py cluster-data.json 4.20 compatibility_matrix.json
```

---

## 🎯 Common Use Cases

### Use Case 1: Customer Planning Upgrade
**Scenario:** Customer wants to upgrade from 4.18 to 4.21

```bash
# In customer's must-gather
cd /path/to/must-gather
geminicli check operator compatibility for OCP 4.21
```

**Result:** List of operators that need upgrades before cluster upgrade

---

### Use Case 2: Cluster Already Upgraded, Some Operators Failing
**Scenario:** Customer upgraded to 4.20, ACM is failing

```bash
geminicli why is ACM incompatible with OCP 4.20?
```

**Result:** Shows ACM version is too old, recommends upgrade to 2.13.10

---

### Use Case 3: Pre-Upgrade Checklist
**Scenario:** Need complete operator audit before upgrade

```bash
geminicli generate upgrade checklist for OCP 4.22
```

**Result:** Full report with all operators, status, and action items

---

## ❓ Troubleshooting

### Issue: "compatibility_matrix.json not found"
**Solution:**
```bash
# Make sure you're in the same directory where you downloaded it
ls -lh compatibility_matrix.json

# If missing, download again
curl -o compatibility_matrix.json https://raw.githubusercontent.com/navaneethas/ocp-operator-upgrade-advisor/main/compatibility_matrix.json
```

### Issue: "No data found in must-gather"
**Solution:**
```bash
# Verify must-gather structure
find . -name "subscriptions" -type d
find . -name "clusterserviceversions" -type d

# Should show paths like:
# ./quay-io.../namespaces/openshift-operators/operators.coreos.com/subscriptions
```

### Issue: Geminicli not recognizing the skill
**Solution:**
```bash
# Make sure the skill file is in the current directory or geminicli skills directory
ls -lh ocp-operator-compatibility.md

# Check geminicli skills location
geminicli --list-skills
```

---

## 📞 Support

If you encounter issues:

1. **Check GitHub for updates:**
   - https://github.com/navaneethas/ocp-operator-upgrade-advisor

2. **Contact the author:**
   - Created by: nsenthil@redhat.com
   - GitHub: https://github.com/nsenthil

3. **Known limitations:**
   - Only covers Red Hat operators (180 operators)
   - OCP versions 4.12 to 4.22
   - Does not check deprecated APIs or other upgrade blockers

---

## 🔄 Updating the Skill

To get the latest version:

```bash
# Download latest skill file
curl -o ocp-operator-compatibility.md https://raw.githubusercontent.com/navaneethas/ocp-operator-upgrade-advisor/main/ocp-operator-compatibility.md

# Download latest compatibility matrix (updated monthly)
curl -o compatibility_matrix.json https://raw.githubusercontent.com/navaneethas/ocp-operator-upgrade-advisor/main/compatibility_matrix.json
```

---

## ✅ Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│  Supportshell - Operator Compatibility Check            │
│  (Geminicli Skill)                                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1️⃣  Setup (one time):                                   │
│     curl -o ocp-operator-compatibility.md \              │
│       https://raw.githubusercontent.com/nsenthil/\       │
│       ocp-upgrade-advisor/main/\                         │
│       ocp-operator-compatibility.md                      │
│                                                          │
│     curl -o compatibility_matrix.json \                  │
│       https://raw.githubusercontent.com/nsenthil/\       │
│       ocp-upgrade-advisor/main/\                         │
│       compatibility_matrix.json                          │
│                                                          │
│  2️⃣  Use (every case):                                    │
│     cd /path/to/must-gather                              │
│     geminicli check operators for OCP 4.20               │
│                                                          │
│  3️⃣  Results:                                             │
│     ✓ Compatible → No action                             │
│     ⚠ Upgrade Required → See recommended version         │
│     ✗ Incompatible → Contact Red Hat                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📚 Additional Resources

- **Web UI:** https://navaneethas.github.io/ocp-operator-upgrade-advisor/
- **GitHub Repo:** https://github.com/navaneethas/ocp-operator-upgrade-advisor
- **Full Documentation:** See README.md in the repo

---

**Created with ❤️ to make operator upgrades easier in supportshell!**

**Last Updated:** August 2026
**Version:** 1.0.0
**Author:** nsenthil@redhat.com
