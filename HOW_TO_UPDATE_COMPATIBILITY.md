# How to Update the Compatibility Matrix

## 🎯 Understanding the Compatibility Matrix

The compatibility decisions are based on **`COMPATIBILITY_MATRIX`** in `backend/simple_server.py`.

### Location
**File**: `backend/simple_server.py`  
**Lines**: 17-66

### Current Issue
The matrix is **manually maintained** with **example data**. For production use, you need to populate it with **real Red Hat compatibility data**.

---

## 📊 How the Matrix Works

### Structure
```python
COMPATIBILITY_MATRIX = {
    "operator-package-name": {
        "4.21": ["1.0", "1.1", "1.2"],  # Supported versions
        "4.20": ["0.9", "1.0", "1.1"],
    }
}
```

### Example
```python
"cluster-logging": {
    "4.21": ["6.5", "6.6"],  # OCP 4.21 supports logging 6.5 and 6.6
}
```

### How It's Used

**Your Input:**
- Operator: `cluster-logging`
- Current Version: `6.5.1`
- Target OCP: `4.21`

**Backend Logic:**
1. Look up `cluster-logging` in matrix
2. Find entry for `"4.21"` → `["6.5", "6.6"]`
3. Check if `6.5.1` starts with `6.5` or `6.6`
4. Result: ✅ **COMPATIBLE** (matches `6.5`)

---

## 🔍 Where to Find Real Compatibility Data

### 1. **Red Hat Operator Hub**
https://catalog.redhat.com/software/containers/explore

Search for your operator and check:
- Supported OpenShift versions
- Compatible operator versions
- Lifecycle information

### 2. **Operator Documentation**
For each operator, check official docs:

**GitOps:**
https://docs.openshift.com/gitops/latest/release_notes/gitops-release-notes.html

**Cluster Logging:**
https://docs.openshift.com/container-platform/latest/logging/cluster-logging-release-notes.html

**Quay:**
https://access.redhat.com/documentation/en-us/red_hat_quay/

### 3. **PackageManifest from Your Cluster**
Run on your cluster:
```bash
oc get packagemanifest <operator-name> -o yaml
```

Look for:
- `channels` → supported versions per channel
- `currentCSV` → latest version
- Check CSV annotations for `olm.properties` with version support

### 4. **Red Hat Support Matrix**
https://access.redhat.com/support/policy/updates/openshift_operators

Official lifecycle and compatibility matrices.

### 5. **OperatorHub.io**
https://operatorhub.io/

Community-driven operator information.

---

## 🛠️ How to Update the Matrix

### Step 1: Identify Your Operators

Run this on your cluster to see what you have:
```bash
oc get csv -A -o json | jq -r '.items[].spec | "\(.displayName): \(.version)"'
```

### Step 2: Research Each Operator

For each operator, find:
- Official name (package name)
- Supported versions for each OCP version
- Lifecycle/EOL dates

### Step 3: Update `simple_server.py`

Edit the `COMPATIBILITY_MATRIX`:

```python
COMPATIBILITY_MATRIX = {
    "your-operator-name": {
        "4.18": ["1.0", "1.1"],
        "4.19": ["1.1", "1.2"],
        "4.20": ["1.2", "1.3"],
        "4.21": ["1.3", "1.4"],
    },
}
```

### Step 4: Restart Backend

```bash
# Stop current backend
ps aux | grep simple_server.py | grep -v grep | awk '{print $2}' | xargs kill

# Start with updates
cd backend
python3 simple_server.py
```

### Step 5: Test

Upload your cluster data and verify:
- No false positives (compatible shown as incompatible)
- No false negatives (incompatible shown as compatible)

---

## 📝 Real Example: GitOps Operator

### Research Process

**Step 1**: Check Red Hat Docs
https://docs.openshift.com/gitops/latest/release_notes/gitops-release-notes.html

**Step 2**: Find Version Matrix

| GitOps Version | Supported OCP Versions |
|----------------|----------------------|
| 1.18 | 4.19, 4.20 |
| 1.19 | 4.20, 4.21 |
| 1.20 | 4.20, 4.21 |
| 1.21 | 4.21 |

**Step 3**: Convert to Matrix Format

```python
"gitops-operator": {
    "4.19": ["1.18"],
    "4.20": ["1.18", "1.19", "1.20"],
    "4.21": ["1.19", "1.20", "1.21"],
}
```

---

## 🔄 Automated Updates (Future)

### Option 1: Query OperatorHub API

```python
import requests

def fetch_operator_versions(operator_name):
    url = f"https://operatorhub.io/api/operator?packageName={operator_name}"
    response = requests.get(url)
    # Parse and build matrix
    return versions
```

### Option 2: Parse PackageManifest Dynamically

```python
def build_matrix_from_cluster(packagemanifest_json):
    # Extract channels and versions
    # Build compatibility matrix on-the-fly
    pass
```

### Option 3: Use Red Hat API

```python
# Red Hat Ecosystem Catalog API
def query_redhat_catalog(operator):
    # Query official Red Hat data
    pass
```

---

## ⚠️ Important Notes

### 1. **Operator Name Matching**

The system matches by **package name**, not display name:

**Package Name** (used in matrix):
```python
"cluster-logging"  # Correct
```

**Display Name** (NOT used):
```python
"Red Hat OpenShift Logging"  # Wrong
```

**How to Find Package Name:**
```bash
oc get subscription -A -o json | jq -r '.items[] | .spec.name'
```

### 2. **Version Prefix Matching**

The system uses **prefix matching**:

**Matrix Entry:**
```python
"4.21": ["6.5", "6.6"]
```

**Matches:**
- ✅ `6.5`
- ✅ `6.5.1`
- ✅ `6.5.10`
- ✅ `6.6.0`
- ❌ `6.4.9`
- ❌ `6.7.0`

### 3. **Multiple Names for Same Operator**

Some operators have multiple package names:

```python
COMPATIBILITY_MATRIX = {
    "gitops-operator": { ... },           # Name 1
    "openshift-gitops-operator": { ... }, # Name 2 (same data)
}
```

---

## 🎯 Quick Fix for Your Issue

**Your Error:**
```
openshift-gitops-operator version 1.21.1 is not supported on OpenShift 4.21
```

**Cause:**
Matrix had `"4.21": ["1.18", "1.19", "1.20"]` but your version is `1.21.1`

**Fix Applied:**
```python
"4.21": ["1.18", "1.19", "1.20", "1.21"]  # Added 1.21
```

**Now Try Again:**
1. Refresh browser
2. Re-upload your data
3. Analyze
4. Should show **COMPATIBLE** ✅

---

## 📋 Template for New Operator

```python
# Add this to COMPATIBILITY_MATRIX in simple_server.py

"your-operator-package-name": {
    "4.12": ["x.y"],           # Find from Red Hat docs
    "4.13": ["x.y", "x.z"],
    "4.14": ["x.z", "a.b"],
    "4.15": ["a.b", "a.c"],
    "4.16": ["a.c", "a.d"],
    "4.17": ["a.d", "a.e"],
    "4.18": ["a.e", "a.f"],
    "4.19": ["a.f", "a.g"],
    "4.20": ["a.g", "a.h"],
    "4.21": ["a.h", "a.i"],
},
```

---

## 🎓 Best Practices

1. **Always include major.minor** (e.g., `1.21` not `1.21.1`)
   - System uses prefix matching
   - `1.21` matches `1.21.0`, `1.21.1`, `1.21.99`

2. **Include overlapping versions**
   - If an operator works on both 4.20 and 4.21, list it in both

3. **Keep matrix updated**
   - Check quarterly for new releases
   - Monitor operator lifecycle announcements

4. **Test with real data**
   - Use actual cluster exports
   - Verify against Red Hat documentation

5. **Document your sources**
   - Add comments with doc URLs
   ```python
   # Source: https://docs.openshift.com/gitops/latest/release_notes/
   "gitops-operator": { ... }
   ```

---

## 📊 Verification Checklist

After updating the matrix:

- [ ] All your cluster operators are in the matrix
- [ ] Versions match Red Hat documentation
- [ ] No false UNSUPPORTED warnings
- [ ] Backend restarts without errors
- [ ] Test analysis shows expected results
- [ ] Documented sources for future reference

---

## 🚀 Next Steps

1. **Update with your operators**: Add all operators from your cluster
2. **Verify accuracy**: Cross-check with Red Hat docs
3. **Restart backend**: Apply changes
4. **Re-analyze**: Upload cluster data again
5. **Document**: Keep notes on where you found the data

---

**Last Updated**: July 25, 2026  
**Status**: Backend updated with GitOps 1.21 support  
**Action Required**: Refresh browser and re-analyze
