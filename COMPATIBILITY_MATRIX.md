# OpenShift Compatibility Matrix

## Current Support

The application now supports **OpenShift versions 4.12 through 4.21** (Latest as of July 2026).

## Where the Versions Come From

The compatibility matrix is defined in two places:

### 1. Frontend (simple-ui.html)
Location: Lines 648-658

The dropdown menu showing available OpenShift versions:
```html
<select id="targetVersion">
    <option value="4.12">OpenShift 4.12</option>
    <option value="4.13">OpenShift 4.13</option>
    <option value="4.14">OpenShift 4.14</option>
    <option value="4.15">OpenShift 4.15</option>
    <option value="4.16">OpenShift 4.16</option>
    <option value="4.17">OpenShift 4.17</option>
    <option value="4.18">OpenShift 4.18</option>
    <option value="4.19">OpenShift 4.19</option>
    <option value="4.20">OpenShift 4.20</option>
    <option value="4.21" selected>OpenShift 4.21 (Latest)</option>
</select>
```

### 2. Backend (simple_server.py)
Location: Lines 16-63

The compatibility matrix that determines which operator versions work with each OpenShift version:

```python
COMPATIBILITY_MATRIX = {
    "gitops-operator": {
        "4.12": ["1.8", "1.9", "1.10"],
        "4.13": ["1.9", "1.10", "1.11", "1.12"],
        # ... up to 4.21
        "4.21": ["1.18", "1.19", "1.20"],
    },
    "quay-operator": {
        "4.12": ["3.8", "3.9"],
        # ... up to 4.21
        "4.21": ["3.17", "3.18"],
    },
    # Add more operators here
}
```

## Currently Supported Operators

1. **GitOps Operator** (gitops-operator)
   - 4.12 → 4.21: Versions 1.8 through 1.20

2. **Quay Operator** (quay-operator)
   - 4.12 → 4.21: Versions 3.8 through 3.18

3. **Cluster Logging** (cluster-logging)
   - 4.12 → 4.21: Versions 5.6 through 6.6

4. **OpenShift Pipelines** (openshift-pipelines-operator-rh)
   - 4.12 → 4.21: Versions 1.12 through 1.22

## How to Add New Operators

### Step 1: Add to Backend Compatibility Matrix

Edit `backend/simple_server.py` and add your operator to the `COMPATIBILITY_MATRIX`:

```python
COMPATIBILITY_MATRIX = {
    # ... existing operators ...
    
    "your-operator-name": {
        "4.18": ["1.0", "1.1"],
        "4.19": ["1.1", "1.2"],
        "4.20": ["1.2", "1.3"],
        "4.21": ["1.3", "1.4"],
    },
}
```

### Step 2: Restart Backend

```bash
# Kill the old process
ps aux | grep simple_server.py | grep -v grep
kill <PID>

# Start new process
cd backend
python3 simple_server.py
```

### Step 3: Test

Upload cluster data with your operator and verify compatibility checks work.

## How to Add New OpenShift Versions

When a new OpenShift version is released (e.g., 4.22):

### Step 1: Update Frontend Dropdown

Edit `simple-ui.html` and add the new version:

```html
<select id="targetVersion">
    <!-- existing versions -->
    <option value="4.21">OpenShift 4.21</option>
    <option value="4.22" selected>OpenShift 4.22 (Latest)</option>
</select>
```

### Step 2: Update Backend Compatibility Matrix

Edit `simple_server.py` and add the new version to each operator:

```python
COMPATIBILITY_MATRIX = {
    "gitops-operator": {
        # ... existing versions ...
        "4.21": ["1.18", "1.19", "1.20"],
        "4.22": ["1.19", "1.20", "1.21"],  # NEW
    },
    "quay-operator": {
        # ... existing versions ...
        "4.21": ["3.17", "3.18"],
        "4.22": ["3.18", "3.19"],  # NEW
    },
}
```

### Step 3: Restart & Test

```bash
# Restart backend
kill <PID> && python3 simple_server.py

# Refresh browser (Cmd+R)
# Test with the new version
```

## Data Source for Compatibility

The compatibility matrix is currently **manually curated** based on:

1. **Red Hat Operator Documentation**
   - Official operator support matrices
   - Release notes
   - Lifecycle pages

2. **OperatorHub Metadata**
   - PackageManifest data from OperatorHub
   - CSV annotations
   - Channel information

3. **Community Knowledge**
   - Known working combinations
   - Tested configurations

## Future Enhancements

### Automatic Matrix Updates

In the future, the application could:

1. **Query OperatorHub API** to fetch latest compatibility data
2. **Parse Red Hat Documentation** automatically
3. **Use PackageManifest** from the cluster itself for dynamic compatibility
4. **Crowdsource Data** from user submissions

### Dynamic Version Loading

Instead of hardcoded versions, fetch from:
- OpenShift release API
- Red Hat version metadata
- GitHub releases

## Example: Adding Advanced Cluster Security Operator

```python
# In backend/simple_server.py

COMPATIBILITY_MATRIX = {
    # ... existing operators ...
    
    "advanced-cluster-security": {
        "4.18": ["4.0", "4.1"],
        "4.19": ["4.1", "4.2"],
        "4.20": ["4.2", "4.3"],
        "4.21": ["4.3", "4.4"],
    },
}
```

Then restart backend and test!

## Troubleshooting

### "Operator not found in matrix"

Your operator isn't in the `COMPATIBILITY_MATRIX`. Add it manually.

### "No supported versions for target OCP"

The operator doesn't have an entry for that OpenShift version. Update the matrix.

### Versions seem outdated

The matrix is manually maintained. Update `simple_server.py` with latest versions.

## Contributing

To contribute operator compatibility data:

1. Test operator on specific OpenShift version
2. Document working version combinations
3. Update `COMPATIBILITY_MATRIX` in `simple_server.py`
4. Submit a pull request (if using git)

---

**Last Updated**: July 25, 2026  
**Latest OpenShift Version**: 4.21  
**Total Operators in Matrix**: 4 (GitOps, Quay, Logging, Pipelines)
