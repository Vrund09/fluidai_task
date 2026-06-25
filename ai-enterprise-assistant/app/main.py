from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.models import AskRequest, AskResponse
from app.agent import run as agent_run
from app.guardrails import check as guardrails_check

app = FastAPI(title="AI Enterprise Assistant")

INDEX_HTML = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/")
async def root():
    return HTMLResponse(INDEX_HTML)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/ask")
async def ask(body: AskRequest) -> AskResponse:
    ok, reason = guardrails_check(body.question)
    if not ok:
        return AskResponse(
            answer=reason,
            action_taken=None,
            action_result=None,
            metadata={
                "model": "guardrail",
                "latency_ms": 0,
                "fallback_used": False,
                "tool_calls": 0,
            },
        )

    result = agent_run(body.question)
    return AskResponse(
        answer=result["answer"],
        action_taken=result["action_taken"],
        action_result=result["action_result"],
        metadata=result["metadata"],
    )
