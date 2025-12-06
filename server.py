"""HTTP server for running the Agent in Kubernetes or any container runtime.

Exposes a simple REST API:
- GET  /healthz   -> basic health check
- POST /chat      -> run the agent on a user query

This avoids interactive CLI and is suitable for k8s deployments.
"""

import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from monitoring.langfuse_config import setup_langfuse
from agents.base_agent import create_agent_with_monitoring
from utils.helpers import extract_final_answer, get_trace_id, get_observation_id


class ChatRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    answer: str
    raw_result: Any
    trace_id: str
    observation_id: str


app = FastAPI(title="LangChain Agent + Langfuse API", version="1.0.0")


_langfuse_ok = False
_agent = None


def _bool_env(name: str, default: bool = True) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).lower() in {"1", "true", "yes", "on"}


def _ensure_initialized() -> None:
    global _langfuse_ok, _agent
    if _agent is not None:
        return

    # Initialize Langfuse (non-fatal on network/config errors in server mode)
    try:
        setup_langfuse()
        _langfuse_ok = True
    except Exception:
        # In restricted networks this can fail; healthz will reflect status
        _langfuse_ok = False

    model_type = os.getenv("MODEL_TYPE", "deepseek")
    model_name = os.getenv("MODEL_NAME") or ("deepseek-chat" if model_type == "deepseek" else "gpt-4o")
    enable_intent = _bool_env("ENABLE_INTENT_CLASSIFICATION", True)

    _agent = create_agent_with_monitoring(
        model_type=model_type,
        model_name=model_name,
        system_prompt=(
            "你是一个有用的 AI 助手，可以帮助用户查询文档、获取天气信息和进行数学计算。"
        ),
        enable_intent_classification=enable_intent,
    )


@app.get("/healthz")
def healthz() -> Dict[str, Any]:
    # Lazy init to ensure healthz can also create the agent if needed
    _ensure_initialized()
    return {
        "status": "ok",
        "langfuse_connected": _langfuse_ok,
        "agent_ready": _agent is not None,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    _ensure_initialized()
    assert _agent is not None, "Agent not initialized"

    result = _agent.invoke_with_error_handling(
        query=req.query,
        user_id=req.user_id,
        session_id=req.session_id,
        tags=req.tags or ["api"],
        metadata=req.metadata or {"source": "http"},
    )

    answer = extract_final_answer(result)

    return ChatResponse(
        answer=answer,
        raw_result=result,
        trace_id=get_trace_id(),
        observation_id=get_observation_id(),
    )


if __name__ == "__main__":
    # For local test: python server.py
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=_bool_env("RELOAD", False),
    )

