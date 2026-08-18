from fastapi import APIRouter, HTTPException
from typing import Dict
import uuid
from datetime import datetime

from app.models import (
    AnalysisRequest,
    AnalysisResponse,
    ClusterInfo,
    CompatibilityStatus
)
from app.parsers import (
    parse_clusterversion,
    parse_subscriptions,
    parse_csvs,
    parse_catalogsources,
    parse_packagemanifests
)
from app.services.operator_discovery import discover_operators
from app.services.compatibility import check_operator_compatibility, calculate_risk_level
from app.services.ai import generate_executive_summary, explain_compatibility

router = APIRouter()

analysis_cache: Dict[str, AnalysisResponse] = {}

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_cluster(request: AnalysisRequest):
    """
    Analyze cluster operators for compatibility with target OpenShift version.

    Args:
        request: Analysis request with JSON data

    Returns:
        Analysis results with compatibility status and recommendations
    """
    try:
        cluster_version = parse_clusterversion(request.clusterversion_json)
        subscriptions = parse_subscriptions(request.subscriptions_json)
        csvs = parse_csvs(request.csv_json)
        catalogsources = parse_catalogsources(request.catalogsource_json)
        packagemanifests = parse_packagemanifests(request.packagemanifest_json)

        operators = discover_operators(
            subscriptions,
            csvs,
            catalogsources,
            packagemanifests
        )

        compatibility_results = []
        upgrade_paths = {}

        for operator in operators:
            result = check_operator_compatibility(
                operator,
                request.target_ocp_version,
                csvs
            )

            if result.upgrade_path:
                upgrade_paths[operator.name] = result.upgrade_path

            compatibility_results.append(result)

        compatible_count = sum(
            1 for r in compatibility_results
            if r.status == CompatibilityStatus.COMPATIBLE
        )
        upgrade_required_count = sum(
            1 for r in compatibility_results
            if r.status == CompatibilityStatus.UPGRADE_REQUIRED
        )
        unsupported_count = sum(
            1 for r in compatibility_results
            if r.status == CompatibilityStatus.UNSUPPORTED
        )
        manual_count = sum(
            1 for r in compatibility_results
            if r.status == CompatibilityStatus.MANUAL_INTERVENTION
        )

        cluster_info = ClusterInfo(
            current_version=cluster_version.version,
            target_version=request.target_ocp_version,
            total_operators=len(operators),
            compatible_count=compatible_count,
            upgrade_required_count=upgrade_required_count,
            unsupported_count=unsupported_count,
            manual_count=manual_count
        )

        risk_score = calculate_risk_level(compatibility_results)

        for result in compatibility_results:
            operator = next((op for op in operators if op.name == result.operator_name), None)
            if operator and not result.explanation:
                result.explanation = explain_compatibility(operator, result)

        ai_summary = generate_executive_summary(cluster_info, compatibility_results)

        analysis_id = str(uuid.uuid4())

        response = AnalysisResponse(
            analysis_id=analysis_id,
            timestamp=datetime.now(),
            cluster_info=cluster_info,
            operators=operators,
            compatibility_results=compatibility_results,
            upgrade_paths=upgrade_paths,
            ai_summary=ai_summary,
            risk_score=risk_score
        )

        analysis_cache[analysis_id] = response

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str):
    """
    Retrieve a previously completed analysis.

    Args:
        analysis_id: UUID of the analysis

    Returns:
        Analysis results
    """
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis_cache[analysis_id]
