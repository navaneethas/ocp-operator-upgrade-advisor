#!/bin/bash
#
# OpenShift Operator Compatibility Matrix Generator
# Uses oc-mirror to build a complete compatibility matrix for all operators
#

set -e

# Configuration
OCP_VERSIONS=(4.12 4.13 4.14 4.15 4.16 4.17 4.18 4.19 4.20 4.21 4.22)
CATALOGS=(
    "redhat-operator-index"
    "certified-operator-index"
    "community-operator-index"
    "redhat-marketplace-index"
)
OUTPUT_FILE="compatibility_matrix.json"
TEMP_DIR="./oc-mirror-temp"

# Create temp directory
mkdir -p "$TEMP_DIR"

echo "🚀 Starting OpenShift Operator Compatibility Matrix Generation"
echo "=============================================================="
echo ""

# Initialize JSON output
echo "{" > "$OUTPUT_FILE"

# Track if we need a comma
first_operator=true

# Total progress tracking
total_steps=0
current_step=0

# Calculate total steps
echo "📊 Calculating total work..."
for ocp_version in "${OCP_VERSIONS[@]}"; do
    for catalog in "${CATALOGS[@]}"; do
        total_steps=$((total_steps + 1))
    done
done

echo "   Total catalogs to process: $total_steps"
echo ""

# Process each OCP version
for ocp_version in "${OCP_VERSIONS[@]}"; do
    echo "=================================================="
    echo "Processing OpenShift ${ocp_version}"
    echo "=================================================="

    # Get all operators from all catalogs for this OCP version
    declare -A operators_map

    for catalog in "${CATALOGS[@]}"; do
        current_step=$((current_step + 1))
        catalog_url="registry.redhat.io/redhat/${catalog}:v${ocp_version}"

        echo ""
        echo "[$current_step/$total_steps] 📦 Catalog: ${catalog}"
        echo "   URL: ${catalog_url}"

        # List all operators in this catalog
        operator_list_file="${TEMP_DIR}/${ocp_version}_${catalog}_operators.txt"

        echo "   ⏳ Fetching operator list..."
        if oc-mirror list operators --catalog "${catalog_url}" --v2 2>&1 | \
           grep -A 1000 "^NAME" | tail -n +2 | grep -v "^$" > "${operator_list_file}"; then

            operator_count=$(wc -l < "${operator_list_file}")
            echo "   ✅ Found ${operator_count} operators"

            # Process each operator
            while IFS= read -r line; do
                # Extract operator name (first column)
                operator_name=$(echo "$line" | awk '{print $1}')

                if [ -z "$operator_name" ]; then
                    continue
                fi

                # Store operator name for processing
                operators_map["$operator_name"]=1

            done < "${operator_list_file}"
        else
            echo "   ⚠️  Failed to fetch operators from ${catalog}"
        fi
    done

    echo ""
    echo "📋 Processing ${#operators_map[@]} unique operators for OCP ${ocp_version}..."

    # Now get detailed channel info for each operator
    operator_num=0
    for operator_name in "${!operators_map[@]}"; do
        operator_num=$((operator_num + 1))

        # Progress indicator
        if [ $((operator_num % 50)) -eq 0 ]; then
            echo "   Processed ${operator_num}/${#operators_map[@]} operators..."
        fi

        # Try each catalog until we find the operator
        found=false
        for catalog in "${CATALOGS[@]}"; do
            catalog_url="registry.redhat.io/redhat/${catalog}:v${ocp_version}"

            # Get channel details for this operator
            channel_file="${TEMP_DIR}/${ocp_version}_${operator_name}_channels.txt"

            if oc-mirror list operators \
                --catalog "${catalog_url}" \
                --package "${operator_name}" \
                --v2 2>&1 | \
                grep -A 1000 "^PACKAGE" | tail -n +2 | grep -v "^$" > "${channel_file}" 2>/dev/null; then

                if [ -s "${channel_file}" ]; then
                    found=true

                    # Extract versions from HEAD column
                    versions=()
                    while IFS= read -r channel_line; do
                        # HEAD is the third column
                        head_csv=$(echo "$channel_line" | awk '{print $3}')

                        # Extract version from CSV name (e.g., "servicemeshoperator3.v3.4.0" -> "3.4.0")
                        if [[ "$head_csv" =~ \.v([0-9]+\.[0-9]+(\.[0-9]+)?) ]]; then
                            version="${BASH_REMATCH[1]}"
                            versions+=("$version")
                        fi
                    done < "${channel_file}"

                    # Remove duplicates and sort
                    if [ ${#versions[@]} -gt 0 ]; then
                        versions=($(printf '%s\n' "${versions[@]}" | sort -u))

                        # Add to JSON (if first time seeing this operator)
                        if ! grep -q "\"${operator_name}\":" "$OUTPUT_FILE"; then
                            # Add comma if not first operator
                            if [ "$first_operator" = false ]; then
                                echo "," >> "$OUTPUT_FILE"
                            fi
                            first_operator=false

                            # Start operator entry
                            echo "  \"${operator_name}\": {" >> "$OUTPUT_FILE"
                        fi

                        # Add OCP version entry
                        # Check if we need to add comma
                        if grep -q "\"${operator_name}\":" "$OUTPUT_FILE" && \
                           grep -A 100 "\"${operator_name}\":" "$OUTPUT_FILE" | grep -q "\"4\."; then
                            echo "," >> "$OUTPUT_FILE"
                        fi

                        # Write versions as JSON array
                        echo -n "    \"${ocp_version}\": [" >> "$OUTPUT_FILE"
                        for i in "${!versions[@]}"; do
                            echo -n "\"${versions[$i]}\"" >> "$OUTPUT_FILE"
                            if [ $i -lt $((${#versions[@]} - 1)) ]; then
                                echo -n ", " >> "$OUTPUT_FILE"
                            fi
                        done
                        echo -n "]" >> "$OUTPUT_FILE"
                    fi

                    break  # Found in this catalog, no need to check others
                fi
            fi
        done

        if [ "$found" = false ]; then
            echo "   ⚠️  Operator ${operator_name} not found in any catalog for OCP ${ocp_version}"
        fi
    done

    echo "   ✅ Completed OCP ${ocp_version}"
done

# Close all open operator objects and main JSON
echo "" >> "$OUTPUT_FILE"
echo "  }" >> "$OUTPUT_FILE"
echo "}" >> "$OUTPUT_FILE"

# Clean up temp directory
echo ""
echo "🧹 Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

echo ""
echo "=============================================================="
echo "✅ Compatibility matrix generation complete!"
echo "📄 Output saved to: ${OUTPUT_FILE}"
echo ""
echo "📊 Statistics:"
operator_count=$(grep -c "\":" "$OUTPUT_FILE" | head -1 || echo "0")
echo "   Operators processed: ${operator_count}"
echo "   OCP versions: ${#OCP_VERSIONS[@]}"
echo "   File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo ""
echo "🎯 Next steps:"
echo "   1. Review the generated JSON file"
echo "   2. Embed it into cli-analyzer-universal.py"
echo "   3. Test with sample cluster data"
echo ""
