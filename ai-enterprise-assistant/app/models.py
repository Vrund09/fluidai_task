from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class AskResponse(BaseModel):
    answer: str
    action_taken: str | None = None
    action_result: dict | None = None
    metadata: dict
