from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, Response, JSONResponse
from app.api.analysis import analysis_cache
from jinja2 import Template
import json

router = APIRouter()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>OpenShift Operator Upgrade Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #ee0000;
            color: white;
            padding: 20px;
            border-radius: 5px;
        }
        .section {
            background-color: white;
            margin: 20px 0;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .summary-card {
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .summary-card h3 {
            margin: 0;
            font-size: 2em;
        }
        .summary-card p {
            margin: 5px 0 0 0;
            color: #666;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f8f8;
            font-weight: bold;
        }
        .status-compatible { color: #28a745; }
        .status-upgrade { color: #ffc107; }
        .status-manual { color: #ff9800; }
        .status-unsupported { color: #dc3545; }
        .risk-low { background-color: #d4edda; }
        .risk-medium { background-color: #fff3cd; }
        .risk-high { background-color: #f8d7da; }
        .risk-critical { background-color: #f5c6cb; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenShift Operator Upgrade Report</h1>
        <p>Generated: {{ timestamp }}</p>
    </div>

    <div class="section">
        <h2>Cluster Information</h2>
        <p><strong>Current Version:</strong> {{ cluster_info.current_version }}</p>
        <p><strong>Target Version:</strong> {{ cluster_info.target_version }}</p>
        <p><strong>Risk Level:</strong> <span class="risk-{{ risk_score }}">{{ risk_score | upper }}</span></p>
    </div>

    <div class="section">
        <h2>Summary</h2>
        <div class="summary-grid">
            <div class="summary-card risk-low">
                <h3>{{ cluster_info.compatible_count }}</h3>
                <p>Compatible</p>
            </div>
            <div class="summary-card risk-medium">
                <h3>{{ cluster_info.upgrade_required_count }}</h3>
                <p>Upgrade Required</p>
            </div>
            <div class="summary-card risk-high">
                <h3>{{ cluster_info.manual_count }}</h3>
                <p>Manual Intervention</p>
            </div>
            <div class="summary-card risk-critical">
                <h3>{{ cluster_info.unsupported_count }}</h3>
                <p>Unsupported</p>
            </div>
        </div>
    </div>

    {% if ai_summary %}
    <div class="section">
        <h2>AI Analysis</h2>
        <p>{{ ai_summary }}</p>
    </div>
    {% endif %}

    <div class="section">
        <h2>Operator Compatibility</h2>
        <table>
            <thead>
                <tr>
                    <th>Operator</th>
                    <th>Current Version</th>
                    <th>Target Version</th>
                    <th>Status</th>
                    <th>Explanation</th>
                </tr>
            </thead>
            <tbody>
                {% for result in compatibility_results %}
                <tr>
                    <td>{{ result.operator_name }}</td>
                    <td>{{ result.current_version }}</td>
                    <td>{{ result.target_version or 'N/A' }}</td>
                    <td class="status-{{ result.status }}">{{ result.status | replace('_', ' ') | title }}</td>
                    <td>{{ result.explanation or 'No explanation available' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    {% if upgrade_paths %}
    <div class="section">
        <h2>Upgrade Paths</h2>
        {% for name, path in upgrade_paths.items() %}
        <div style="margin: 15px 0;">
            <h3>{{ name }}</h3>
            <p><strong>Path:</strong> {{ ' → '.join(path.path) }}</p>
            <p><strong>Steps:</strong> {{ path.steps }}</p>
            <p>{{ path.description }}</p>
        </div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
"""

@router.get("/{analysis_id}/html", response_class=HTMLResponse)
async def get_html_report(analysis_id: str):
    """Generate HTML report for analysis."""
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = analysis_cache[analysis_id]

    template = Template(HTML_TEMPLATE)
    html = template.render(
        timestamp=analysis.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        cluster_info=analysis.cluster_info,
        risk_score=analysis.risk_score,
        ai_summary=analysis.ai_summary,
        compatibility_results=analysis.compatibility_results,
        upgrade_paths=analysis.upgrade_paths
    )

    return HTMLResponse(content=html)

@router.get("/{analysis_id}/json")
async def get_json_report(analysis_id: str):
    """Export analysis as JSON."""
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = analysis_cache[analysis_id]
    return JSONResponse(content=json.loads(analysis.model_dump_json()))

@router.get("/{analysis_id}/pdf")
async def get_pdf_report(analysis_id: str):
    """Generate PDF report (placeholder for now)."""
    raise HTTPException(
        status_code=501,
        detail="PDF generation not yet implemented. Use HTML export for now."
    )
