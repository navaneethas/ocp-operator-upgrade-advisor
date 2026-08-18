# Single Command Usage Guide

## 🎯 One Command to Rule Them All!

Instead of running 5 separate commands and uploading 5 files, now you can use **ONE command** to generate a single file with all required data.

## 📦 The Magic Command

Copy and paste this **entire command** into your OpenShift cluster terminal:

```bash
(echo '{"clusterVersion":'; oc get clusterversion version -o json; echo ',"subscriptions":'; oc get sub -A -o json; echo ',"clusterServiceVersions":'; oc get csv -A -o json; echo ',"catalogSources":'; oc get catalogsource -A -o json; echo ',"packageManifests":'; oc get packagemanifest -o json; echo '}') > openshift-data.json
```

This creates a single file: **`openshift-data.json`**

## ✨ What This Does

The command:
1. Opens a subshell with `()`
2. Echoes JSON structure markers
3. Runs all 5 `oc` commands
4. Combines their output into valid JSON
5. Saves to `openshift-data.json`

## 📂 File Structure

The generated `openshift-data.json` contains:

```json
{
  "clusterVersion": { /* oc get clusterversion version -o json */ },
  "subscriptions": { /* oc get sub -A -o json */ },
  "clusterServiceVersions": { /* oc get csv -A -o json */ },
  "catalogSources": { /* oc get catalogsource -A -o json */ },
  "packageManifests": { /* oc get packagemanifest -o json */ }
}
```

## 🚀 Usage Steps

### Step 1: Connect to Your Cluster

```bash
oc login https://your-cluster-api:6443
```

### Step 2: Run the Single Command

```bash
(echo '{"clusterVersion":'; oc get clusterversion version -o json; echo ',"subscriptions":'; oc get sub -A -o json; echo ',"clusterServiceVersions":'; oc get csv -A -o json; echo ',"catalogSources":'; oc get catalogsource -A -o json; echo ',"packageManifests":'; oc get packagemanifest -o json; echo '}') > openshift-data.json
```

### Step 3: Verify the File

```bash
# Check file was created
ls -lh openshift-data.json

# Validate JSON
cat openshift-data.json | jq . > /dev/null && echo "✅ Valid JSON"
```

### Step 4: Download the File

If running on a remote cluster:

```bash
# Using scp
scp user@cluster:/path/to/openshift-data.json .

# Or just copy the content
cat openshift-data.json
```

### Step 5: Upload to the Advisor

1. Open http://localhost:5173 (or open `index.html`)
2. Drag & drop `openshift-data.json`
3. Select target OpenShift version
4. Click "Analyze Compatibility"

## 💡 Why Single File?

### Old Way (5 files):
```bash
oc get clusterversion version -o json > clusterversion.json
oc get sub -A -o json > subscriptions.json
oc get csv -A -o json > csv.json
oc get catalogsource -A -o json > catalogsource.json
oc get packagemanifest -o json > packagemanifest.json
```
Then upload 5 separate files

### New Way (1 file):
```bash
(echo '{"clusterVersion":'; oc get clusterversion version -o json; ...) > openshift-data.json
```
Upload 1 file

**Benefits:**
- ✅ Faster - one command instead of five
- ✅ Simpler - one file instead of five
- ✅ Less error-prone - can't forget a file
- ✅ Easier to share - send one file

## 🔧 Alternative: Multi-Line Version

If you prefer readability, use this multi-line version:

```bash
(
  echo '{"clusterVersion":'
  oc get clusterversion version -o json
  echo ',"subscriptions":'
  oc get sub -A -o json
  echo ',"clusterServiceVersions":'
  oc get csv -A -o json
  echo ',"catalogSources":'
  oc get catalogsource -A -o json
  echo ',"packageManifests":'
  oc get packagemanifest -o json
  echo '}'
) > openshift-data.json
```

## 📊 Sample File

A sample file is included in `sample-data/openshift-data.json`:

```bash
cd /Users/nsenthil/AI_TOOL/openshift-upgrade-advisor
cat sample-data/openshift-data.json
```

This contains data for a sample OpenShift 4.19 cluster with GitOps and Quay operators.

## 🎨 UI Features

The new single-file UI includes:

- **Drag & Drop**: Just drag the file onto the upload zone
- **One-Click Copy**: Click "📋 Copy" to copy the command
- **Visual Feedback**: Upload zone changes color when file is loaded
- **Same Analysis**: All the same features as the 5-file version

## 🔄 Backward Compatibility

The backend still supports the old 5-file format:

```json
{
  "clusterversion_json": { },
  "subscriptions_json": { },
  "csv_json": { },
  "catalogsource_json": { },
  "packagemanifest_json": { },
  "target_ocp_version": "4.21"
}
```

So the old `simple-ui.html` still works!

## 🐛 Troubleshooting

### Command fails with "permission denied"

Make sure you're logged into OpenShift:
```bash
oc whoami
```

### JSON validation fails

The command uses `echo` to build JSON. Make sure you copied the **entire** command including the parentheses.

### File is too large

This is normal for clusters with many operators. The file can be several MB. The application handles large files.

### Missing data in file

Run this to check what's included:
```bash
cat openshift-data.json | jq 'keys'
```

Should show:
```json
[
  "catalogSources",
  "clusterServiceVersions",
  "clusterVersion",
  "packageManifests",
  "subscriptions"
]
```

## 📱 Quick Reference Card

```
╔════════════════════════════════════════════════════════════╗
║  OpenShift Operator Upgrade Advisor - Quick Reference     ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  1. Login to cluster:                                      ║
║     oc login https://your-cluster:6443                     ║
║                                                            ║
║  2. Generate data file (ONE COMMAND):                      ║
║     (echo '{"clusterVersion":';                            ║
║      oc get clusterversion version -o json;                ║
║      echo ',"subscriptions":';                             ║
║      oc get sub -A -o json;                                ║
║      echo ',"clusterServiceVersions":';                    ║
║      oc get csv -A -o json;                                ║
║      echo ',"catalogSources":';                            ║
║      oc get catalogsource -A -o json;                      ║
║      echo ',"packageManifests":';                          ║
║      oc get packagemanifest -o json;                       ║
║      echo '}') > openshift-data.json                       ║
║                                                            ║
║  3. Upload to: http://localhost:5173                       ║
║     or open index.html                                     ║
║                                                            ║
║  4. Analyze!                                               ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

## 🎓 Pro Tips

1. **Add to your .bashrc**:
   ```bash
   alias ocp-data='(echo "{\"clusterVersion\":"; oc get clusterversion version -o json; echo ",\"subscriptions\":"; oc get sub -A -o json; echo ",\"clusterServiceVersions\":"; oc get csv -A -o json; echo ",\"catalogSources\":"; oc get catalogsource -A -o json; echo ",\"packageManifests\":"; oc get packagemanifest -o json; echo "}") > openshift-data.json'
   ```
   
   Then just run: `ocp-data`

2. **Include cluster name**:
   ```bash
   CLUSTER=$(oc whoami --show-server | cut -d'/' -f3 | cut -d':' -f1)
   (echo '{"clusterVersion":'; ...) > "openshift-data-${CLUSTER}.json"
   ```

3. **Add timestamp**:
   ```bash
   DATE=$(date +%Y%m%d-%H%M%S)
   (echo '{"clusterVersion":'; ...) > "openshift-data-${DATE}.json"
   ```

4. **Pipe through jq for formatting**:
   ```bash
   (echo '{"clusterVersion":'; ...; echo '}') | jq '.' > openshift-data.json
   ```

---

**Last Updated**: July 25, 2026  
**File Format Version**: 1.0  
**Compatible with**: OpenShift 4.12 - 4.21
