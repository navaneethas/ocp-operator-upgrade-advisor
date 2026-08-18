# Must-Gather Environment Guide

## ✅ Simplified for Must-Gather

In must-gather environments, you typically don't have access to `packagemanifest`. **That's OK!** The analyzer only needs three things:

1. ✅ **clusterVersion** - Current OCP version
2. ✅ **subscriptions** - Installed operators  
3. ✅ **clusterServiceVersions** - Operator versions

---

## 🚀 Simplified Data Collection

### For JSON Format (if `-o json` works):

```bash
(echo '{"cluster_data":'; \
 echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; \
 echo '  "subscriptions":'; oc get sub -A -o json; echo ','; \
 echo '  "clusterServiceVersions":'; oc get csv -A -o json; echo ','; \
 echo '  "catalogSources":'; oc get catalogsource -A -o json; echo ','; \
 echo '  "packageManifests": {"items": []}'; \
 echo '}') > openshift-data.json
```

### For YAML Format (if outputs YAML):

```bash
(echo 'cluster_data:'; \
 echo '  clusterVersion:'; oc get clusterversion version -o yaml | sed 's/^/    /'; \
 echo '  subscriptions:'; oc get sub -A -o yaml | sed 's/^/    /'; \
 echo '  clusterServiceVersions:'; oc get csv -A -o yaml | sed 's/^/    /'; \
 echo '  catalogSources:'; oc get catalogsource -A -o yaml | sed 's/^/    /'; \
 echo '  packageManifests:'; \
 echo '    items: []') > openshift-data.yaml
```

**Notice:** We just set `packageManifests` to an empty array `[]` - the analyzer will work fine!

---

## 🎯 What If Some Commands Fail?

### Minimum Required Data

At the bare minimum, you need:

```bash
# JSON Format
(echo '{"cluster_data":'; \
 echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; \
 echo '  "subscriptions":'; oc get sub -A -o json; echo ','; \
 echo '  "clusterServiceVersions":'; oc get csv -A -o json; \
 echo '}') > openshift-data.json
```

```bash
# YAML Format  
(echo 'cluster_data:'; \
 echo '  clusterVersion:'; oc get clusterversion version -o yaml | sed 's/^/    /'; \
 echo '  subscriptions:'; oc get sub -A -o yaml | sed 's/^/    /'; \
 echo '  clusterServiceVersions:'; oc get csv -A -o yaml | sed 's/^/    /') > openshift-data.yaml
```

**This is all you need for compatibility analysis!**

---

## 📋 Using Existing Must-Gather Data

If you already have a must-gather archive, you can extract the data from there:

### Option 1: Extract from Must-Gather Files

Must-gather typically stores data in directories like:
```
must-gather.local.XXXXX/
├── cluster-scoped-resources/
│   └── config.openshift.io/
│       └── clusterversions/
└── namespaces/
    └── */
        └── operators.coreos.com/
            ├── subscriptions/
            └── clusterserviceversions/
```

Create a script to collect from must-gather:

```bash
#!/bin/bash
# collect-from-must-gather.sh

MUST_GATHER_DIR="$1"  # Path to must-gather directory

if [ -z "$MUST_GATHER_DIR" ]; then
    echo "Usage: $0 <must-gather-directory>"
    exit 1
fi

# Find clusterversion
CV_FILE=$(find "$MUST_GATHER_DIR" -path "*/clusterversions/version.yaml" | head -1)

# Find subscriptions (all namespaces)
SUB_FILES=$(find "$MUST_GATHER_DIR" -path "*/subscriptions/*.yaml")

# Find CSVs (all namespaces)
CSV_FILES=$(find "$MUST_GATHER_DIR" -path "*/clusterserviceversions/*.yaml")

# Combine into single YAML file
(
    echo 'cluster_data:'
    
    echo '  clusterVersion:'
    cat "$CV_FILE" | sed 's/^/    /'
    
    echo '  subscriptions:'
    echo '    items:'
    for sub in $SUB_FILES; do
        echo '      -'
        cat "$sub" | sed 's/^/        /'
    done
    
    echo '  clusterServiceVersions:'
    echo '    items:'
    for csv in $CSV_FILES; do
        echo '      -'
        cat "$csv" | sed 's/^/        /'
    done
    
) > openshift-data.yaml

echo "✓ Created openshift-data.yaml from must-gather"
```

**Usage:**
```bash
chmod +x collect-from-must-gather.sh
./collect-from-must-gather.sh /path/to/must-gather.local.XXXXX
```

---

## 🔧 Manual Collection (If `oc` Commands Don't Work)

If you can't run `oc` commands, manually create a YAML file:

```yaml
cluster_data:
  clusterVersion:
    spec:
      channel: stable-4.19
      clusterID: your-cluster-id
    status:
      desired:
        version: 4.19.8
  subscriptions:
    items:
      - metadata:
          name: gitops-subscription
          namespace: openshift-gitops
        spec:
          name: openshift-gitops-operator
          channel: stable
        status:
          currentCSV: openshift-gitops-operator.v1.16.2
      # Add more subscriptions...
  clusterServiceVersions:
    items:
      - metadata:
          name: openshift-gitops-operator.v1.16.2
          namespace: openshift-gitops
        spec:
          version: 1.16.2
          displayName: Red Hat OpenShift GitOps
      # Add more CSVs...
```

---

## ✅ What Gets Analyzed

With this minimal data, the analyzer will:

1. ✅ **Identify all installed operators** (from subscriptions)
2. ✅ **Get current operator versions** (from CSVs)
3. ✅ **Check compatibility** against target OpenShift version
4. ✅ **Recommend upgrade versions**
5. ✅ **Calculate risk assessment**

### What You Won't Get (Without PackageManifest)

- ⚠️ Detailed step-by-step upgrade paths (which intermediate versions to go through)
- ⚠️ Skip range information

**But the core compatibility analysis works perfectly!**

---

## 🎨 Example: Minimal Analysis

**Input File (openshift-data.yaml):**
```yaml
cluster_data:
  clusterVersion:
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
    items:
      - metadata:
          name: advanced-cluster-management.v2.13.9
        spec:
          version: 2.13.9
```

**Run Analysis:**
```bash
python3 analyzer.py openshift-data.yaml --target-ocp 4.21
```

**Output:**
```
Cluster Information:
  Current Version:  4.19.8
  Target Version:   4.21
  Total Operators:  1

[1] advanced-cluster-management
  Current Version:    2.13.9
  Status:             ⚠ Incompatible Upgrade Required
  Recommended:        2.17
  Explanation: Requires upgrade to version 2.17 for OpenShift 4.21
```

**Works perfectly!** ✅

---

## 📝 Quick Reference

### Minimum Data Needed

| Resource | Required? | Purpose |
|----------|-----------|---------|
| clusterVersion | ✅ YES | Get current OCP version |
| subscriptions | ✅ YES | List installed operators |
| clusterServiceVersions | ✅ YES | Get operator versions |
| catalogSources | ❌ Optional | Not used in analysis |
| packageManifests | ❌ Optional | Only for detailed upgrade paths |

### Collection Commands

**Minimum (3 resources):**
```bash
# JSON
(echo '{"cluster_data":'; \
 echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; \
 echo '  "subscriptions":'; oc get sub -A -o json; echo ','; \
 echo '  "clusterServiceVersions":'; oc get csv -A -o json; \
 echo '}') > openshift-data.json
```

**With optional resources:**
```bash
# JSON (includes catalogsources, empty packagemanifests)
(echo '{"cluster_data":'; \
 echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; \
 echo '  "subscriptions":'; oc get sub -A -o json; echo ','; \
 echo '  "clusterServiceVersions":'; oc get csv -A -o json; echo ','; \
 echo '  "catalogSources":'; oc get catalogsource -A -o json; echo ','; \
 echo '  "packageManifests": {"items": []}'; \
 echo '}') > openshift-data.json
```

---

## 🎯 Summary

✅ **PackageManifest is NOT required!**  
✅ **Only 3 resources needed** (clusterVersion, subscriptions, CSVs)  
✅ **Works in must-gather environments**  
✅ **Full compatibility analysis without packageManifest**  

**You're good to go!** 🚀
