#!/bin/bash
# Generate copy-paste instructions for supportshell

echo "=========================================================================="
echo "  COPY-PASTE INSTRUCTIONS FOR SUPPORTSHELL"
echo "=========================================================================="
echo ""
echo "Step 1: Create the analyzer script"
echo "------------------------------------"
echo "Copy and paste this ENTIRE block into your supportshell terminal:"
echo ""
echo "cat > analyzer.py << 'SCRIPT_END'"
cat cli-analyzer-standalone.py
echo "SCRIPT_END"
echo ""
echo "=========================================================================="
echo "Step 2: Collect cluster data"
echo "------------------------------------"
echo "Copy and paste this command:"
echo ""
cat << 'DATA_CMD'
(echo '{"cluster_data":'; \
 echo '  "clusterVersion":'; oc get clusterversion version -o json; echo ','; \
 echo '  "subscriptions":'; oc get sub -A -o json; echo ','; \
 echo '  "clusterServiceVersions":'; oc get csv -A -o json; echo ','; \
 echo '  "catalogSources":'; oc get catalogsource -A -o json; echo ','; \
 echo '  "packageManifests":'; oc get packagemanifest -o json; \
 echo '}') > openshift-data.json
DATA_CMD
echo ""
echo "=========================================================================="
echo "Step 3: Run the analysis"
echo "------------------------------------"
echo "Copy and paste this command (replace 4.21 with your target version):"
echo ""
echo "python3 analyzer.py openshift-data.json --target-ocp 4.21"
echo ""
echo "=========================================================================="
echo "Done! The analysis will appear in your terminal."
echo "=========================================================================="
