import os
import logging
import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("Please set the OPENAI_API_KEY environment variable.")

INTENTS = ["cancel_order", "track_order", "product_information", "unknown"]

intent_agent = Agent(
    name="IntentDetector",
    instructions=f"Classify user intent into one of: {', '.join(INTENTS)}. Return ONLY the label."
                 f"For return-related queries, return the label `product_information`.",
    model=OpenAIChatCompletionsModel(model="gpt-4.1-mini", openai_client=AsyncOpenAI(api_key=api_key)),
)


async def detect_intent(session_id: str, message: str) -> str:
    try:
        result = await Runner.run(intent_agent, input=message, conversation_id=session_id)
        intent = result.final_output.strip().lower()
        logger.info(f"Detected Intent: {intent}")

        return intent if intent in INTENTS else "unknown"

    except Exception as e:
        logger.error(f"Error during intent detection: {e}", exc_info=True)
        return "unknown"


async def main():
    session_id = "eb7b5b9f-6464-4baf-a294-cf9b3856c0cd"

    print(f"Turn 1 output: {await detect_intent(session_id, 'I have a problem with my order ORD-9999')}")
    print(f"Turn 2 output: {await detect_intent(session_id, 'Actually, just cancel it.')}")


if __name__ == "__main__":
    asyncio.run(main())