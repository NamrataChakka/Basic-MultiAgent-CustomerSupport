import logging
from agents import Runner
from app.utils.misc import extract_order_id
from app.agents.intent_classifier import detect_intent
from app.services.redis_state import SessionState

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self, agent_registry):
        self.agents = agent_registry

    async def route_user_request(self, message: str, state: SessionState):
        session_id = state.session_id
        context = state.context
        pending_intent = context.get("pending_intent")

        updated_context = {}
        intent = None
        # Initialize order_id from context so it's always available
        order_id = context.get("order_id")

        # --- STEP 1: PENDING INTENT LOGIC ---
        if pending_intent:
            new_order_id = extract_order_id(message)

            if new_order_id:
                order_id = new_order_id  # Update local variable
                updated_context["order_id"] = order_id
                updated_context["pending_intent"] = None
                intent = pending_intent
            else:
                return {
                    "response": "Please provide Order ID (ORD-XXXX) to proceed.",
                    "updated_context": {"pending_intent": pending_intent}
                }

        # --- STEP 2: NEW INTENT DETECTION ---
        else:
            intent = await detect_intent(session_id, message)
            extracted_id = extract_order_id(message)

            if extracted_id:
                order_id = extracted_id
                updated_context["order_id"] = order_id

            # Guardrail: Missing ID for specific tasks
            if intent in ["cancel_order", "track_order"] and not order_id:
                return {
                    "response": "Please provide Order ID (ORD-XXXX) to proceed.",
                    "updated_context": {"pending_intent": intent}
                }

        # --- STEP 3: DISPATCH ---
        selected_agent = self.agents.get(intent)

        if not selected_agent:
            logger.warning(f"No specialist agent found for intent: {intent}")
            return {
                "response": f"I'm sorry, I don't have a specialist for '{intent}'. How else can I help?",
                "agent": "Orchestrator",
                "updated_context": updated_context
            }

        try:
            # We use a clean string for input
            run_input = f"User Intent: {intent}. Order ID: {order_id}. Message: {message}"
            logger.info(f"RUN input: {run_input}")

            result = await Runner.run(
                selected_agent,
                input=run_input,
            )

            return {
                "response": result.final_output,
                "agent": f"Orchestrator -> {selected_agent.name}",
                "updated_context": updated_context,
                "handover": True
            }

        except Exception as e:
            logger.error(f"Error running specialist agent {intent}: {e}")
            return {
                "response": "I encountered an error while processing your request.",
                "updated_context": updated_context
            }