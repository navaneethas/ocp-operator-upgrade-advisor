#!/usr/bin/env python3
"""
Parse oc-mirror data and build compatibility matrix
"""

import json
import re
import os
from pathlib import Path
from collections import defaultdict

def extract_version_from_head(head_value):
    """
    Extract version number from HEAD column
    Examples:
      advanced-cluster-management.v2.16.2 -> 2.16.2
      3scale-operator.v0.13.4 -> 0.13.4
      amq-broker-operator.v7.12.7-opr-1-0.1780501200.p -> 7.12.7
    """
    # Match .vX.Y.Z or .vX.Y pattern
    match = re.search(r'\.v(\d+\.\d+(?:\.\d+)?)', head_value)
    if match:
        return match.group(1)
    return None

def parse_packageversions_file(file_path, ocp_version):
    """
    Parse a single packageversions file and extract operator versions
    Returns: dict of {operator_name: [version1, version2, ...]}
    """
    operator_versions = defaultdict(set)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Split by operator sections
    sections = re.split(r'=== Operator: (.+?) ===', content)

    # Process pairs of (operator_name, section_content)
    for i in range(1, len(sections), 2):
        operator_name = sections[i].strip()
        section_content = sections[i + 1] if i + 1 < len(sections) else ""

        # Find the PACKAGE/CHANNEL/HEAD table
        # Look for lines after "PACKAGE" header
        lines = section_content.split('\n')

        in_table = False
        for line in lines:
            # Detect table header
            if 'PACKAGE' in line and 'CHANNEL' in line and 'HEAD' in line:
                in_table = True
                continue

            # End of table
            if in_table and line.strip() == '':
                break

            # Parse table rows
            if in_table and line.strip():
                # Split by whitespace
                parts = line.split()

                # HEAD is typically the last column
                if len(parts) >= 3:
                    head_value = parts[-1]
                    version = extract_version_from_head(head_value)

                    if version:
                        operator_versions[operator_name].add(version)

    return operator_versions

def build_compatibility_matrix(oc_mirror_data_dir):
    """
    Build complete compatibility matrix from all oc-mirror data
    """
    base_dir = Path(oc_mirror_data_dir)

    # Find all version directories
    version_dirs = sorted([d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith('oc-mirror-data-')])

    print(f"Found {len(version_dirs)} OCP version directories")

    # Build matrix: {operator_name: {ocp_version: [versions]}}
    compatibility_matrix = defaultdict(dict)

    for version_dir in version_dirs:
        # Extract OCP version from directory name (e.g., "oc-mirror-data-4.22" -> "4.22")
        ocp_version = version_dir.name.replace('oc-mirror-data-', '')

        # Find packageversions file
        packageversions_file = version_dir / f"packageversions_{ocp_version}.txt"

        if not packageversions_file.exists():
            print(f"⚠️  Warning: {packageversions_file} not found")
            continue

        print(f"Processing OCP {ocp_version}...")

        # Parse file
        operator_versions = parse_packageversions_file(packageversions_file, ocp_version)

        print(f"  Found {len(operator_versions)} operators")

        # Add to matrix
        for operator_name, versions in operator_versions.items():
            # Sort versions
            sorted_versions = sorted(list(versions), key=lambda v: [int(x) for x in v.split('.')])
            compatibility_matrix[operator_name][ocp_version] = sorted_versions

    # Convert defaultdict to regular dict for JSON serialization
    return {k: dict(v) for k, v in compatibility_matrix.items()}

def main():
    # Path to oc-mirror data - UPDATED to upgradeChecker folder
    oc_mirror_data_dir = "/Users/nsenthil/AI_TOOL/upgradeChecker"

    print("=" * 80)
    print("OpenShift Operator Compatibility Matrix Builder")
    print("=" * 80)
    print()

    if not os.path.exists(oc_mirror_data_dir):
        print(f"❌ Error: {oc_mirror_data_dir} not found!")
        return 1

    # Build matrix
    print("Building compatibility matrix...")
    print()

    matrix = build_compatibility_matrix(oc_mirror_data_dir)

    print()
    print("=" * 80)
    print(f"✅ Matrix built successfully!")
    print(f"   Total operators: {len(matrix)}")
    print()

    # Show sample
    print("Sample entries:")
    print("-" * 80)

    sample_operators = ['advanced-cluster-management', 'cluster-logging', 'openshift-gitops-operator']
    for op in sample_operators:
        if op in matrix:
            print(f"\n{op}:")
            for ocp_version in sorted(matrix[op].keys()):
                versions = matrix[op][ocp_version]
                print(f"  {ocp_version}: {versions}")

    # Save to JSON
    output_file = "compatibility_matrix.json"
    print()
    print("-" * 80)
    print(f"Saving to {output_file}...")

    with open(output_file, 'w') as f:
        json.dump(matrix, f, indent=2, sort_keys=True)

    # Get file size
    file_size = os.path.getsize(output_file)

    print(f"✅ Saved successfully!")
    print(f"   File size: {file_size / 1024:.1f} KB")
    print()

    # Statistics
    print("=" * 80)
    print("Statistics:")
    print("-" * 80)

    ocp_versions = set()
    for operator_data in matrix.values():
        ocp_versions.update(operator_data.keys())

    print(f"  Operators: {len(matrix)}")
    print(f"  OCP versions: {sorted(ocp_versions)}")

    # Show operators per OCP version
    print()
    print("  Operators per OCP version:")
    for ocp_version in sorted(ocp_versions):
        count = sum(1 for op_data in matrix.values() if ocp_version in op_data)
        print(f"    {ocp_version}: {count} operators")

    print()
    print("=" * 80)
    print("🎯 Next steps:")
    print("   1. Review compatibility_matrix.json")
    print("   2. Embed it into cli-analyzer-universal.py")
    print("   3. Test with cluster data")
    print("=" * 80)
    print()

    return 0

if __name__ == '__main__':
    exit(main())
