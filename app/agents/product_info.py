import logging
import os

from ..utils.read_write_ops import lookup_product_in_vector_store

from openai import OpenAI
from agents import function_tool, Agent, AsyncOpenAI, OpenAIChatCompletionsModel

logger = logging.getLogger(__name__)

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    logger.info("OpenAI client & vector store initialized successfully.")

except Exception as e:
    logger.error(f"Failed to initialize OpenAI client or vector store. {e}")

ProductInfoAgent = Agent(
    name="ProductInfoAgent",
    instructions="""
        You are an agent that assists with queries regarding products.
        Always use the 'lookup_product_in_vector_store' tool to check for information regarding products.
        Be polite in your responses and do not fabricate information that isn't from the lookup_product_in_vector_store
        tool.
    """,
    model=OpenAIChatCompletionsModel(
        model="gpt-4.1-mini",
        openai_client=AsyncOpenAI()
    ),
    tools=[lookup_product_in_vector_store]
)