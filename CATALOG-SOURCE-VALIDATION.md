# ✅ Catalog Source Validation Added

**Date:** August 7, 2026  
**Feature:** Non-Red Hat Operator Detection  
**Status:** ✅ Complete and Tested

---

## 🎯 Feature Overview

The compatibility checker now validates that operators are from **Red Hat catalogs only**. If an operator is from a certified, community, marketplace, or custom catalog, it displays a clear message explaining that the checker is designed for Red Hat operators only.

---

## 📋 Supported vs Non-Supported Catalogs

### ✅ Supported (Red Hat Operators)
- **`redhat-operators`** - Official Red Hat operators
- **`redhat-operator-index`** - Red Hat operator catalog index

### ❌ Not Supported (Shows Warning)
- **`certified-operators`** - Third-party certified operators
- **`community-operators`** - Community-maintained operators
- **`redhat-marketplace`** - Red Hat Marketplace operators
- **`custom-operators`** - Custom/private operator catalogs

---

## 🔍 How It Works

### 1. Catalog Source Extraction
The tool now extracts the `source` field from operator subscriptions:

```json
{
  "spec": {
    "name": "mongodb-enterprise",
    "channel": "stable",
    "source": "certified-operators",  ← Catalog source
    "sourceNamespace": "openshift-marketplace"
  }
}
```

### 2. Validation Logic
```python
non_redhat_catalogs = [
    'certified-operators',
    'community-operators',
    'redhat-marketplace',
    'custom-operators'
]

if catalog_source in non_redhat_catalogs:
    return "not_redhat_operator" status
```

### 3. User-Friendly Message
Instead of showing "Unknown" or attempting to check compatibility, the tool displays:

> **Sorry, this operator is from Certified Operators. The compatibility checker is currently designed for Red Hat operators only. Please check the operator's documentation for compatibility information.**

---

## 📊 Example Output

### CLI Output

```
[1] mongodb-enterprise
  Current Version:    1.20.0
  Catalog Source:     certified-operators
  Status:             ℹ Not Redhat Operator
  Available in 4.16: (not in catalog)
  
  Explanation: Sorry, this operator is from Certified Operators. 
  The compatibility checker is currently designed for Red Hat operators only. 
  Please check the operator's documentation for compatibility information.

[2] openshift-gitops-operator
  Current Version:    1.10.6
  Catalog Source:     redhat-operators
  Status:             ✓ Compatible
  Max Supported OCP:  4.22
  Available in 4.16: 1.6.6, 1.7.4, 1.8.6, 1.9.4, 1.10.6 ... (16 total)
  
  Explanation: openshift-gitops-operator v1.10.6 is compatible with 
  OpenShift 4.16. Current version supported up to OCP 4.22.
```

### GUI Display

**Non-Red Hat Operator Card:**
```
┌─────────────────────────────────────────────────┐
│ mongodb-enterprise                              │
│                     [NON-RED HAT OPERATOR] ←───┤ Light blue badge
├─────────────────────────────────────────────────┤
│ Current Version:    1.20.0                      │
│ Catalog Source:     certified-operators         │
│ Channel:            stable                      │
├─────────────────────────────────────────────────┤
│ 💡 Recommendation                               │
│ Sorry, this operator is from Certified          │
│ Operators. The compatibility checker is         │
│ currently designed for Red Hat operators only.  │
│ Please check the operator's documentation for   │
│ compatibility information.                      │
└─────────────────────────────────────────────────┘
```

**Red Hat Operator Card (Normal):**
```
┌─────────────────────────────────────────────────┐
│ openshift-gitops-operator                       │
│                            [✓ COMPATIBLE] ←────┤ Green badge
├─────────────────────────────────────────────────┤
│ Current Version:    1.10.6                      │
│ Max Supported OCP:  4.22                        │
│ Recommended:        1.21.1                      │
│ Available in 4.16:  1.6.6, 1.7.4, ... (16)     │
├─────────────────────────────────────────────────┤
│ 💡 Recommendation                               │
│ openshift-gitops-operator v1.10.6 is compatible│
│ with OpenShift 4.16. Current version supported │
│ up to OCP 4.22.                                 │
└─────────────────────────────────────────────────┘
```

---

## 🎨 Visual Indicators

### Status Badges

| Status | Badge Color | Icon | Text |
|--------|-------------|------|------|
| Compatible | Green | ✓ | COMPATIBLE |
| Upgrade Required | Orange | ⚠ | UPGRADE REQUIRED |
| Incompatible | Red | ✗ | INCOMPATIBLE |
| Non-Red Hat | Light Blue | ℹ | NON-RED HAT OPERATOR |
| Unknown | Blue | ? | UNKNOWN |

### CSS Styling
```css
.status-notredhatoperator {
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    color: white;
    border: 2px solid #0dcaf0;
}
```

---

## 🔧 Files Modified

### 1. Backend: `backend/simple_server_enhanced.py`

**Changes:**
- Added `catalog_source` parameter to `check_compatibility()`
- Added non-Red Hat catalog detection logic
- Extract `source` and `sourceNamespace` from subscriptions
- Return `not_redhat_operator` status for non-RH catalogs
- Updated `unknown` status message to mention non-RH operators

**Key Functions:**
```python
def check_compatibility(operator_name, current_version, target_ocp, catalog_source=None):
    # Check if operator is from non-Red Hat catalog
    if catalog_source:
        non_redhat_catalogs = [
            'certified-operators',
            'community-operators',
            'redhat-marketplace',
            'custom-operators'
        ]
        
        for non_rh_catalog in non_redhat_catalogs:
            if non_rh_catalog in catalog_source.lower():
                return "not_redhat_operator" status
```

### 2. CLI: `cli-analyzer-enhanced.py`

**Changes:**
- Added same `catalog_source` parameter logic
- Extract `source` from subscriptions
- Display catalog source in output
- Color-coded status with cyan for non-RH operators
- Hide "Max Supported OCP" for non-RH operators

### 3. GUI: `index.html`

**Changes:**
- Added CSS for `.status-notredhatoperator`
- Added status display mapping: `not_redhat_operator` → `NON-RED HAT OPERATOR`
- Light blue gradient badge for non-RH operators

---

## ✅ Testing Results

### Test Case 1: Mixed Operators

**Input:**
```json
{
  "subscriptions": {
    "items": [
      {
        "spec": {
          "name": "mongodb-enterprise",
          "source": "certified-operators"
        }
      },
      {
        "spec": {
          "name": "openshift-gitops-operator",
          "source": "redhat-operators"
        }
      },
      {
        "spec": {
          "name": "strimzi-kafka-operator",
          "source": "community-operators"
        }
      }
    ]
  }
}
```

**Results:**
1. ✅ **mongodb-enterprise** → Status: `ℹ Not Redhat Operator`
   - Message: "Sorry, this operator is from Certified Operators..."
   - No compatibility check performed

2. ✅ **openshift-gitops-operator** → Status: `✓ Compatible`
   - Full compatibility check performed
   - Shows max OCP, recommended version, etc.

3. ✅ **strimzi-kafka-operator** → Status: `ℹ Not Redhat Operator`
   - Message: "Sorry, this operator is from Community Operators..."
   - No compatibility check performed

---

## 🎯 User Experience Benefits

### Before
```
[1] mongodb-enterprise
  Status: ✗ Unknown
  Explanation: No compatibility data available for mongodb-enterprise.
```
❌ Confusing - user doesn't know why it's unknown

### After
```
[1] mongodb-enterprise
  Catalog Source: certified-operators
  Status: ℹ Not Redhat Operator
  Explanation: Sorry, this operator is from Certified Operators. 
  The compatibility checker is currently designed for Red Hat operators only.
  Please check the operator's documentation for compatibility information.
```
✅ Clear - user knows exactly why and what to do

---

## 📚 User Guidance

### For Non-Red Hat Operators

When users see the "Non-Red Hat Operator" status, they should:

1. **Certified Operators:**
   - Check OperatorHub.io for compatibility info
   - Contact vendor for OCP version support
   - Review operator's documentation

2. **Community Operators:**
   - Check GitHub repository for compatibility matrix
   - Review operator documentation
   - Test in non-production environment

3. **Red Hat Marketplace:**
   - Check marketplace.redhat.com
   - Contact vendor support
   - Review product documentation

4. **Custom Operators:**
   - Contact internal operator team
   - Review internal documentation
   - Test in development environment

---

## 🔄 Future Enhancements

### Potential Additions:

1. **External Links:**
   ```
   For mongodb-enterprise (Certified):
   📚 Documentation: https://operatorhub.io/operator/mongodb-enterprise
   ```

2. **Catalog-Specific Guidance:**
   ```
   For community operators:
   ⚠️  Community operators may not receive Red Hat support.
   Test thoroughly before upgrading OpenShift.
   ```

3. **Catalog Statistics:**
   ```
   Summary:
   - Red Hat Operators: 8
   - Certified Operators: 2
   - Community Operators: 1
   ```

---

## ✅ Summary

**Feature Status:** ✅ Complete and Production-Ready

**Capabilities:**
- ✅ Detects non-Red Hat operators from catalog source
- ✅ Shows clear, helpful messages
- ✅ Distinct visual styling (light blue badge)
- ✅ Works in both CLI and GUI
- ✅ Tested with multiple catalog types

**User Benefits:**
- 🎯 Clear explanation of why operator is not checked
- 🎯 Guidance on where to find compatibility info
- 🎯 No confusion between "unknown" and "non-Red Hat"
- 🎯 Professional user experience

The OpenShift Operator Upgrade Advisor now intelligently handles operators from all catalog sources! 🚀
