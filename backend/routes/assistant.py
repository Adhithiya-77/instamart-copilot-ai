from fastapi import APIRouter
from backend.schemas import AssistantRequest, AssistantResponse
from backend.services.assistant_service import handle

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/chat", response_model=AssistantResponse)
def chat(req: AssistantRequest):
    result = handle(req.message)
    return AssistantResponse(**result)
