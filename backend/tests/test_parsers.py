import pytest
from app.parsers import (
    parse_clusterversion,
    parse_subscriptions,
    parse_csvs,
    parse_catalogsources,
    parse_packagemanifests
)

def test_parse_clusterversion():
    """Test clusterversion parser with sample data."""
    data = {
        "spec": {
            "channel": "stable-4.14",
            "clusterID": "test-cluster-123",
            "upstream": "https://example.com"
        },
        "status": {
            "desired": {
                "version": "4.14.35"
            }
        }
    }

    result = parse_clusterversion(data)

    assert result.version == "4.14.35"
    assert result.channel == "stable-4.14"
    assert result.cluster_id == "test-cluster-123"

def test_parse_subscriptions():
    """Test subscriptions parser with sample data."""
    data = {
        "items": [
            {
                "metadata": {
                    "name": "gitops-sub",
                    "namespace": "openshift-gitops"
                },
                "spec": {
                    "name": "gitops-operator",
                    "channel": "latest",
                    "source": "redhat-operators",
                    "sourceNamespace": "openshift-marketplace"
                },
                "status": {
                    "currentCSV": "gitops-operator.v1.12.0",
                    "installedCSV": "gitops-operator.v1.12.0"
                }
            }
        ]
    }

    results = parse_subscriptions(data)

    assert len(results) == 1
    assert results[0].name == "gitops-sub"
    assert results[0].package == "gitops-operator"
    assert results[0].channel == "latest"
    assert results[0].current_csv == "gitops-operator.v1.12.0"

def test_parse_csvs():
    """Test CSV parser with sample data."""
    data = {
        "items": [
            {
                "metadata": {
                    "name": "gitops-operator.v1.12.0",
                    "namespace": "openshift-gitops",
                    "annotations": {
                        "olm.skipRange": ">=1.10.0 <1.12.0"
                    }
                },
                "spec": {
                    "version": "1.12.0",
                    "displayName": "Red Hat OpenShift GitOps",
                    "description": "GitOps Operator",
                    "replaces": "gitops-operator.v1.11.0",
                    "skips": ["gitops-operator.v1.10.5"]
                }
            }
        ]
    }

    results = parse_csvs(data)

    assert len(results) == 1
    assert results[0].name == "gitops-operator.v1.12.0"
    assert results[0].version == "1.12.0"
    assert results[0].replaces == "gitops-operator.v1.11.0"
    assert results[0].skip_range == ">=1.10.0 <1.12.0"
    assert len(results[0].skips) == 1

def test_parse_empty_items():
    """Test parsers handle empty items list."""
    data = {"items": []}

    assert len(parse_subscriptions(data)) == 0
    assert len(parse_csvs(data)) == 0
    assert len(parse_catalogsources(data)) == 0
    assert len(parse_packagemanifests(data)) == 0
