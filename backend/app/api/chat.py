from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse
from app.api.analysis import analysis_cache
from openai import OpenAI
import os

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Answer questions about analysis results using AI.

    Args:
        request: Chat request with analysis ID and question

    Returns:
        AI-generated answer
    """
    if request.analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis = analysis_cache[request.analysis_id]

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ChatResponse(
            answer="AI chat is not available. Please configure OPENAI_API_KEY.",
            context_used=False
        )

    context = f"""
Cluster: {analysis.cluster_info.current_version} → {analysis.cluster_info.target_version}
Total Operators: {analysis.cluster_info.total_operators}
Compatible: {analysis.cluster_info.compatible_count}
Upgrade Required: {analysis.cluster_info.upgrade_required_count}

Operators:
"""
    for result in analysis.compatibility_results:
        context += f"- {result.operator_name}: {result.current_version} ({result.status})\n"

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an OpenShift expert answering questions about operator upgrade analysis."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {request.question}"}
            ],
            max_tokens=300,
            temperature=0.7
        )

        answer = response.choices[0].message.content.strip()

        return ChatResponse(answer=answer, context_used=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
