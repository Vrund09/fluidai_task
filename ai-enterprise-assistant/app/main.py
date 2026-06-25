from fastapi import FastAPI

from app.models import AskRequest, AskResponse
from app.agent import run as agent_run

app = FastAPI(title="AI Enterprise Assistant")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/ask")
async def ask(body: AskRequest) -> AskResponse:
    result = agent_run(body.question)
    return AskResponse(
        answer=result["answer"],
        action_taken=result["action_taken"],
        action_result=result["action_result"],
        metadata=result["metadata"],
    )
