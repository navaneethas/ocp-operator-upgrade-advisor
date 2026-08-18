#!/bin/bash
#
# Test script - Generate compatibility for a single operator
# Use this to verify the logic before running the full script
#

set -e

OPERATOR="servicemeshoperator3"
OCP_VERSIONS=(4.19 4.20 4.21)
OUTPUT_FILE="test_single_operator.json"

echo "🧪 Testing compatibility matrix generation for: ${OPERATOR}"
echo "=============================================================="
echo ""

echo "{" > "$OUTPUT_FILE"
echo "  \"${OPERATOR}\": {" >> "$OUTPUT_FILE"

first_version=true

for ocp_version in "${OCP_VERSIONS[@]}"; do
    echo "Processing OpenShift ${ocp_version}..."

    catalog_url="registry.redhat.io/redhat/redhat-operator-index:v${ocp_version}"

    # Get operator details
    echo "  Querying: oc-mirror list operators --catalog ${catalog_url} --package ${OPERATOR}"

    temp_file=$(mktemp)

    if oc-mirror list operators \
        --catalog "${catalog_url}" \
        --package "${OPERATOR}" \
        --v2 2>&1 | \
        grep -A 1000 "^PACKAGE" | tail -n +2 | grep -v "^$" > "${temp_file}"; then

        echo "  ✅ Found operator data"

        # Extract versions
        versions=()
        while IFS= read -r line; do
            # HEAD column is the third field
            head_csv=$(echo "$line" | awk '{print $3}')

            # Extract version number from CSV name
            # Example: "servicemeshoperator3.v3.4.0" -> "3.4.0"
            if [[ "$head_csv" =~ \.v([0-9]+\.[0-9]+(\.[0-9]+)?) ]]; then
                version="${BASH_REMATCH[1]}"
                versions+=("$version")
            fi
        done < "${temp_file}"

        # Remove duplicates and sort
        versions=($(printf '%s\n' "${versions[@]}" | sort -u))

        echo "  📦 Versions found: ${versions[*]}"

        # Add to JSON
        if [ "$first_version" = false ]; then
            echo "," >> "$OUTPUT_FILE"
        fi
        first_version=false

        # Write JSON entry
        echo -n "    \"${ocp_version}\": [" >> "$OUTPUT_FILE"
        for i in "${!versions[@]}"; do
            echo -n "\"${versions[$i]}\"" >> "$OUTPUT_FILE"
            if [ $i -lt $((${#versions[@]} - 1)) ]; then
                echo -n ", " >> "$OUTPUT_FILE"
            fi
        done
        echo -n "]" >> "$OUTPUT_FILE"
    else
        echo "  ⚠️  Operator not found in OCP ${ocp_version}"
    fi

    rm -f "${temp_file}"
    echo ""
done

echo "" >> "$OUTPUT_FILE"
echo "  }" >> "$OUTPUT_FILE"
echo "}" >> "$OUTPUT_FILE"

echo "=============================================================="
echo "✅ Test complete!"
echo "📄 Output saved to: ${OUTPUT_FILE}"
echo ""
echo "Preview:"
cat "$OUTPUT_FILE"
echo ""
