from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.agent.orchestrator import AgentOrchestrator
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent import AgentChatRequest, AgentChatResponse

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_agent(
    request: AgentChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Interacts with the Nexus Autonomous Career Intelligence Agent.
    Executes scoped database tools (e.g. search, deadlines, shortlist, skill stats, matches)
    server-side without exposing database access or arbitrary user scoping to the LLM.
    """
    return await AgentOrchestrator.process_chat(
        db=db,
        user_id=current_user.id,
        message=request.message,
        history=request.history,
    )
