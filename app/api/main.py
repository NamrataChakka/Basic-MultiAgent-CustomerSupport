import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import your custom modules
from app.services.redis_session import get_session, save_session
from app.agents.orchestrator import Orchestrator

# Import your specialized agents
from app.agents.order_tracking import OrderTrackingAgent
from app.agents.order_cancellation import OrderCancellationAgent
from app.agents.product_info import ProductInfoAgent

# Setup logging for observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Customer Support Multi-Agent API")


# 1. Input Schema
class ChatRequest(BaseModel):
    session_id: str
    message: str


# 2. Agent Registry
# This mapping allows the Orchestrator to route intents to the right Agent object
AGENT_REGISTRY = {
    "track_order": OrderTrackingAgent,
    "cancel_order": OrderCancellationAgent,
    "product_information": ProductInfoAgent
}


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Primary endpoint for handling user messages.
    Logic Flow:
    1. Load current state from Redis.
    2. Route request through the Orchestrator.
    3. Update state based on Orchestrator feedback.
    4. Persist updated state to Redis.
    """
    try:
        # A. Load state from Redis
        state = get_session(request.session_id)
        logger.info(f"Session {request.session_id} loaded. Current context: {state.context}")

        # B. Initialize and call the Orchestrator
        orchestrator = Orchestrator(AGENT_REGISTRY)
        result = await orchestrator.route_user_request(
            message=request.message,
            state=state
        )

        # C. Update the persistence layer
        # If the orchestrator identified an Order ID or set/cleared a pending intent,
        # we update the state object before saving.
        if "updated_context" in result:
            state.context.update(result["updated_context"])

        # D. Save back to Redis
        save_session(state)
        logger.info(f"Session {request.session_id} updated and saved.")

        # E. Return response to user
        return {
            "session_id": request.session_id,
            "response": result["response"],
            "agent": result.get("agent", "Orchestrator"),
            "handover": result.get("handover", False)
        }

    except Exception as e:
        logger.error(f"Error processing chat for session {request.session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="The AI Assistant is currently unavailable.")
