from typing import List, Optional
from openai import OpenAI
import os
from app.models import CompatibilityResult, OperatorInfo, ClusterInfo

client = None

def get_ai_client():
    """Get or create OpenAI client."""
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            client = OpenAI(api_key=api_key)
    return client

def explain_compatibility(
    operator: OperatorInfo,
    compatibility_result: CompatibilityResult
) -> str:
    """
    Generate AI explanation for operator compatibility status.

    Args:
        operator: Operator information
        compatibility_result: Compatibility check result

    Returns:
        Natural language explanation
    """
    ai_client = get_ai_client()

    if not ai_client:
        return generate_fallback_explanation(operator, compatibility_result)

    prompt = f"""
You are an OpenShift expert. Explain the compatibility status of this operator:

Operator: {operator.name}
Current Version: {compatibility_result.current_version}
Status: {compatibility_result.status}
Supported Versions: {', '.join(compatibility_result.supported_versions) if compatibility_result.supported_versions else 'None'}
Target Version: {compatibility_result.target_version or 'N/A'}

Provide a concise 2-3 sentence explanation of:
1. Why this operator has this compatibility status
2. What action is needed (if any)
3. Any risks or considerations

Keep it professional and focused on actionable information.
"""

    try:
        response = ai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an OpenShift operator compatibility expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"AI explanation failed: {e}")
        return generate_fallback_explanation(operator, compatibility_result)

def generate_executive_summary(
    cluster_info: ClusterInfo,
    compatibility_results: List[CompatibilityResult]
) -> str:
    """
    Generate executive summary of upgrade readiness.

    Args:
        cluster_info: Cluster information
        compatibility_results: All compatibility results

    Returns:
        Executive summary
    """
    ai_client = get_ai_client()

    if not ai_client:
        return generate_fallback_summary(cluster_info, compatibility_results)

    prompt = f"""
You are an OpenShift expert generating an executive summary for an upgrade readiness assessment.

Cluster Information:
- Current OpenShift Version: {cluster_info.current_version}
- Target OpenShift Version: {cluster_info.target_version}
- Total Operators: {cluster_info.total_operators}
- Compatible: {cluster_info.compatible_count}
- Upgrade Required: {cluster_info.upgrade_required_count}
- Unsupported: {cluster_info.unsupported_count}
- Manual Intervention: {cluster_info.manual_count}

Generate a professional executive summary (4-5 sentences) covering:
1. Overall upgrade readiness assessment
2. Key findings
3. Recommended approach
4. Risk level

Be concise, professional, and actionable.
"""

    try:
        response = ai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an OpenShift upgrade planning expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"AI summary failed: {e}")
        return generate_fallback_summary(cluster_info, compatibility_results)

def generate_remediation_steps(
    incompatible_operators: List[CompatibilityResult]
) -> str:
    """
    Generate remediation steps for incompatible operators.

    Args:
        incompatible_operators: List of incompatible operator results

    Returns:
        Remediation steps
    """
    if not incompatible_operators:
        return "All operators are compatible. No remediation needed."

    steps = ["Recommended Remediation Steps:\n"]

    for idx, op in enumerate(incompatible_operators, 1):
        if op.upgrade_path:
            steps.append(
                f"{idx}. {op.operator_name}: Upgrade from {op.current_version} to "
                f"{op.target_version} (Path: {' → '.join(op.upgrade_path.path)})"
            )
        else:
            steps.append(
                f"{idx}. {op.operator_name}: Manual intervention required - "
                f"no direct upgrade path from {op.current_version}"
            )

    return "\n".join(steps)

def generate_fallback_explanation(
    operator: OperatorInfo,
    compatibility_result: CompatibilityResult
) -> str:
    """Generate fallback explanation when AI is unavailable."""
    status = compatibility_result.status

    if status == "compatible":
        return (
            f"{operator.name} version {compatibility_result.current_version} is "
            f"compatible with the target OpenShift version. No action required."
        )
    elif status == "upgrade_required":
        return (
            f"{operator.name} version {compatibility_result.current_version} requires "
            f"an upgrade to {compatibility_result.target_version} for compatibility. "
            f"An upgrade path is available."
        )
    elif status == "manual_intervention":
        return (
            f"{operator.name} version {compatibility_result.current_version} requires "
            f"manual intervention. No automatic upgrade path found to "
            f"{compatibility_result.target_version}."
        )
    else:
        return (
            f"{operator.name} version {compatibility_result.current_version} is "
            f"unsupported for the target OpenShift version."
        )

def generate_fallback_summary(
    cluster_info: ClusterInfo,
    compatibility_results: List[CompatibilityResult]
) -> str:
    """Generate fallback summary when AI is unavailable."""
    total = cluster_info.total_operators
    compatible = cluster_info.compatible_count
    upgrade_required = cluster_info.upgrade_required_count

    if upgrade_required == 0:
        readiness = "Ready"
        action = "All operators are compatible. The cluster is ready for upgrade."
    elif upgrade_required <= 2:
        readiness = "Nearly Ready"
        action = f"{upgrade_required} operator(s) require upgrades before proceeding."
    else:
        readiness = "Not Ready"
        action = f"{upgrade_required} operators require upgrades. Complete operator upgrades before cluster upgrade."

    return (
        f"Upgrade Readiness: {readiness}. "
        f"The cluster contains {total} installed operators. "
        f"{compatible} are already compatible with the target version. "
        f"{action}"
    )
