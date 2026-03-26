import os
from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI
from ..utils.read_write_ops import order_cancellation_process

api_key = os.getenv("OPENAI_API_KEY")

OrderCancellationAgent = Agent(
    name="OrderCancellationAgent",
    instructions="""
        You are an agent that assists with Order Cancellation.
        Always use the 'order_cancellation_process' tool to check eligibility of the order for cancellation.
        If the tool says it's too late (over 24h since the order was placed), politely explain the policy.
        If successful, provide the refund confirmation details.
    """,
    model=OpenAIChatCompletionsModel(
        model="gpt-4.1-mini",
        openai_client=AsyncOpenAI(api_key=api_key)
    ),
    tools=[order_cancellation_process]
)