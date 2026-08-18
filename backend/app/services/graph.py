import networkx as nx
import re
from typing import List, Optional, Tuple
from app.models import CSV, PackageManifest, UpgradePath

def parse_version(version_str: str) -> Tuple[int, ...]:
    """
    Parse version string into tuple for comparison.

    Args:
        version_str: Version string (e.g., "1.12.0", "v1.12.0")

    Returns:
        Tuple of integers for version comparison
    """
    version_str = version_str.lstrip('v')
    parts = re.split(r'[.-]', version_str)

    numeric_parts = []
    for part in parts:
        if part.isdigit():
            numeric_parts.append(int(part))
        else:
            break

    return tuple(numeric_parts) if numeric_parts else (0,)

def version_in_range(version: str, range_str: str) -> bool:
    """
    Check if version falls within skipRange.

    Args:
        version: Version to check
        range_str: Range string (e.g., ">=1.10.0 <1.14.0")

    Returns:
        True if version is in range
    """
    try:
        version_tuple = parse_version(version)

        if '>=' in range_str and '<' in range_str:
            parts = range_str.split()
            min_version = parse_version(parts[0].replace('>=', ''))
            max_version = parse_version(parts[1].replace('<', ''))
            return min_version <= version_tuple < max_version

        return False
    except Exception:
        return False

def build_upgrade_graph(csvs: List[CSV]) -> nx.DiGraph:
    """
    Build directed graph from CSV metadata.

    Nodes: CSV versions
    Edges: replaces, skips, olm.skipRange

    Args:
        csvs: List of CSV objects with upgrade metadata

    Returns:
        NetworkX directed graph
    """
    graph = nx.DiGraph()

    for csv in csvs:
        if not csv.name or not csv.version:
            continue

        graph.add_node(csv.version, csv_name=csv.name, data=csv)

        if csv.replaces:
            replaced_version = extract_version_from_csv_name(csv.replaces)
            if replaced_version:
                graph.add_edge(replaced_version, csv.version, edge_type='replaces')

        if csv.skips:
            for skipped in csv.skips:
                skipped_version = extract_version_from_csv_name(skipped)
                if skipped_version:
                    graph.add_edge(skipped_version, csv.version, edge_type='skips')

        if csv.skip_range:
            for node in list(graph.nodes()):
                if node != csv.version and version_in_range(node, csv.skip_range):
                    graph.add_edge(node, csv.version, edge_type='skipRange')

    return graph

def extract_version_from_csv_name(csv_name: str) -> Optional[str]:
    """
    Extract version from CSV name (e.g., "gitops-operator.v1.12.0" -> "1.12.0")

    Args:
        csv_name: Full CSV name

    Returns:
        Version string or None
    """
    match = re.search(r'v?(\d+\.\d+\.\d+)', csv_name)
    return match.group(1) if match else None

def find_upgrade_path(
    graph: nx.DiGraph,
    current_version: str,
    target_version: str
) -> Optional[List[str]]:
    """
    Find shortest upgrade path from current to target version.

    Args:
        graph: Upgrade graph
        current_version: Starting version
        target_version: Target version

    Returns:
        List of versions in upgrade path, or None if no path exists
    """
    if current_version not in graph:
        return None

    if target_version not in graph:
        return None

    if current_version == target_version:
        return [current_version]

    try:
        path = nx.shortest_path(graph, current_version, target_version)
        return path
    except nx.NetworkXNoPath:
        return None

def build_upgrade_path_model(
    operator_name: str,
    current_version: str,
    target_version: str,
    path: List[str]
) -> UpgradePath:
    """
    Build UpgradePath model from path data.

    Args:
        operator_name: Name of operator
        current_version: Starting version
        target_version: Target version
        path: List of versions in path

    Returns:
        UpgradePath model
    """
    steps = len(path) - 1

    if steps == 0:
        description = f"Already at target version {target_version}"
    elif steps == 1:
        description = f"Direct upgrade from {current_version} to {target_version}"
    else:
        description = f"Upgrade path requires {steps} steps through intermediate versions"

    return UpgradePath(
        operator_name=operator_name,
        current_version=current_version,
        target_version=target_version,
        path=path,
        steps=steps,
        description=description
    )

def get_latest_version_for_operator(csvs: List[CSV], operator_base_name: str) -> Optional[str]:
    """
    Get the latest version for an operator from available CSVs.

    Args:
        csvs: List of all CSVs
        operator_base_name: Base name of operator (without version)

    Returns:
        Latest version string or None
    """
    matching_csvs = [csv for csv in csvs if operator_base_name in csv.name]

    if not matching_csvs:
        return None

    versions = [(parse_version(csv.version), csv.version) for csv in matching_csvs if csv.version]

    if not versions:
        return None

    versions.sort(reverse=True)
    return versions[0][1]
