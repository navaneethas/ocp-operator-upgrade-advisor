# Operator Status Terminology

## 🎯 Status Definitions

### ✅ **COMPATIBLE**
**What it means:**
- Operator version IS supported on target OpenShift version
- No action required

**Color:** 🟢 Green  
**Risk Level:** Low

**Example:**
- Operator: `cluster-logging`
- Current Version: `6.5.1`
- Target OCP: `4.21`
- Matrix has: `"4.21": ["6.5", "6.6"]`
- Result: ✅ **COMPATIBLE** (6.5.1 starts with "6.5")

**Recommendation:**
> "cluster-logging version 6.5.1 is compatible with OpenShift 4.21. No action required."

---

### ⚠️ **UPGRADE REQUIRED**
**What it means:**
- Current operator version is NOT supported on target OCP
- BUT newer compatible versions exist
- Upgrade path available

**Color:** 🟡 Yellow  
**Risk Level:** Medium

**Example:**
- Operator: `gitops-operator`
- Current Version: `1.18.0`
- Target OCP: `4.21`
- Matrix has: `"4.21": ["1.19", "1.20", "1.21"]`
- Result: ⚠️ **UPGRADE REQUIRED**

**Recommendation:**
> "gitops-operator requires upgrade from 1.18.0 to 1.21 for OpenShift 4.21."

---

### ❌ **INCOMPATIBLE** (New!)
**What it means:**
- Current operator version is NOT supported on target OCP
- No compatible versions exist in target OCP
- The operator version you have is too old OR the OCP version is too new
- Shows the maximum OCP version this operator supports

**Color:** 🟠 Orange/Pink  
**Risk Level:** High/Critical

**Example:**
- Operator: `gitops-operator`
- Current Version: `1.12.0`
- Target OCP: `4.21`
- Matrix check: `"4.21"` doesn't include `1.12`
- Find max OCP: `1.12` is supported up to `4.14`
- Result: ❌ **INCOMPATIBLE**

**Recommendation (New Format):**
> "gitops-operator version 1.12.0 is incompatible with OpenShift 4.21. This operator version is supported up to OpenShift 4.14."

**What user should do:**
- Upgrade operator to newer version BEFORE upgrading OCP
- OR stay on older OCP version
- Check operator lifecycle/EOL status

---

### 🔴 **UNSUPPORTED** (Rare - for unknown operators)
**What it means:**
- Operator not found in compatibility matrix at all
- No compatibility information available
- Truly unknown/unsupported operator

**Color:** 🔴 Dark Red  
**Risk Level:** Critical

**Example:**
- Operator: `custom-operator`
- Not in `COMPATIBILITY_MATRIX`
- Result: 🔴 **UNSUPPORTED**

**Recommendation:**
> "custom-operator version X.Y.Z is incompatible with OpenShift 4.21. No compatibility information found for this operator."

---

## 📊 Key Differences

### Before (Old Terminology):
| Status | Meaning | Issue |
|--------|---------|-------|
| Compatible | ✅ Works | ✓ |
| Upgrade Required | ⚠️ Need upgrade | ✓ |
| **Unsupported** | ❌ Won't work | ❌ Confusing term |

### After (New Terminology):
| Status | Meaning | Better? |
|--------|---------|---------|
| Compatible | ✅ Works on target OCP | ✓ |
| Upgrade Required | ⚠️ Need operator upgrade | ✓ |
| **Incompatible** | ❌ Operator version too old for target OCP | ✅ Clear! |
| Unsupported | 🔴 Unknown operator | ✅ Reserved for truly unknown |

---

## 🎨 Visual Indicators

### Status Colors:

**Compatible:**
```css
background: linear-gradient(135deg, #11998e, #38ef7d); /* Green */
```

**Upgrade Required:**
```css
background: linear-gradient(135deg, #f093fb, #f5576c); /* Pink */
```

**Incompatible:**
```css
background: linear-gradient(135deg, #fa709a, #fee140); /* Orange-Yellow */
```

**Unsupported:**
```css
background: linear-gradient(135deg, #dc3545, #c82333); /* Dark Red */
```

---

## 📝 Recommendation Format

### For COMPATIBLE:
```
{operator} version {version} is compatible with OpenShift {ocp_version}.
```

### For UPGRADE REQUIRED:
```
{operator} requires upgrade from {current_version} to {target_version} for OpenShift {ocp_version}.
```

### For INCOMPATIBLE (NEW):
```
{operator} version {current_version} is incompatible with OpenShift {ocp_version}. 
This operator version is supported up to OpenShift {max_ocp_version}.
```

### For UNSUPPORTED:
```
{operator} version {version} is incompatible with OpenShift {ocp_version}. 
No compatibility information found for this operator.
```

---

## 🔧 Backend Implementation

### Status Detection Logic:

```python
def check_compatibility(operator_name, current_version, target_ocp):
    supported_versions = get_supported_versions(operator_name, target_ocp)
    
    # Check 1: Is current version compatible?
    if is_compatible(current_version, supported_versions):
        return "compatible"
    
    # Check 2: Do compatible versions exist?
    if supported_versions:
        return "upgrade_required"  # Yes, user needs to upgrade operator
    
    # Check 3: What's the max OCP version for this operator version?
    max_ocp = find_max_supported_ocp_version(operator_name, current_version)
    
    if max_ocp:
        return "incompatible"  # Show max supported OCP
    else:
        return "unsupported"  # Unknown operator
```

### Max OCP Version Finder:

```python
def find_max_supported_ocp_version(operator_name, current_version):
    """
    Find the highest OCP version that supports this operator version
    """
    for ocp_version in sorted(all_ocp_versions, reverse=True):
        supported = get_supported_versions(operator_name, ocp_version)
        if current_version in supported:
            return ocp_version
    return None
```

---

## 📋 Example Scenarios

### Scenario 1: Old Operator, New OCP

**Input:**
- Operator: `gitops-operator`
- Current: `1.10.0`
- Target OCP: `4.21`

**Matrix Check:**
- `4.21`: supports `["1.19", "1.20", "1.21"]`
- `1.10` not in list
- Find max OCP for `1.10`: Found in `4.14`

**Output:**
```json
{
  "status": "incompatible",
  "max_supported_ocp": "4.14",
  "explanation": "gitops-operator version 1.10.0 is incompatible with OpenShift 4.21. This operator version is supported up to OpenShift 4.14."
}
```

**User Action:**
Upgrade operator from 1.10 → 1.21 BEFORE upgrading OCP to 4.21

---

### Scenario 2: Compatible Version

**Input:**
- Operator: `cluster-logging`
- Current: `6.5.1`
- Target OCP: `4.21`

**Matrix Check:**
- `4.21`: supports `["6.5", "6.6"]`
- `6.5.1` starts with `6.5` ✓

**Output:**
```json
{
  "status": "compatible",
  "explanation": "cluster-logging version 6.5.1 is compatible with OpenShift 4.21."
}
```

**User Action:**
None - ready to upgrade!

---

### Scenario 3: Upgrade Required

**Input:**
- Operator: `quay-operator`
- Current: `3.15.0`
- Target OCP: `4.21`

**Matrix Check:**
- `4.21`: supports `["3.17", "3.18"]`
- `3.15` not in list
- But list is not empty

**Output:**
```json
{
  "status": "upgrade_required",
  "target_version": "3.18",
  "explanation": "quay-operator requires upgrade from 3.15.0 to 3.18 for OpenShift 4.21."
}
```

**User Action:**
Upgrade operator: 3.15 → 3.18

---

## 🎯 Summary of Changes

### What Changed:

1. ✅ **Renamed "UNSUPPORTED" → "INCOMPATIBLE"**
   - More accurate terminology
   - "Unsupported" reserved for unknown operators

2. ✅ **Added Max Supported OCP Version**
   - Shows highest OCP version that supports operator
   - Helps users understand compatibility limits

3. ✅ **Improved Recommendations**
   - Clear actionable guidance
   - Shows compatibility ceiling

4. ✅ **Better Visual Distinction**
   - Orange for incompatible (actionable)
   - Dark red for unsupported (unknown)

### User Benefits:

- ✅ Clearer what the issue is
- ✅ Know the max supported OCP version
- ✅ Better decision making
- ✅ More actionable recommendations

---

**Last Updated**: July 25, 2026  
**Status**: Implemented in both UIs (index.html and simple-ui.html)  
**Backend**: Updated with max OCP version detection
