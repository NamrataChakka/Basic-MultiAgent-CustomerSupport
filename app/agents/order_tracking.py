import os
from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI
from app.utils.read_write_ops import order_tracking_process

api_key = os.getenv("OPENAI_API_KEY")


OrderTrackingAgent = Agent(
    name="OrderTrackingAgent",
    instructions="""
        You are an agent that assists with Order Tracking.
        Always use the 'order_tracking_process' tool to check order validity, current status and delivery date.
        Provide the order ID to the tool.
        After you get the tool output, summarize the status for the user.
    """,
    model=OpenAIChatCompletionsModel(
        model="gpt-4.1-mini",
        openai_client=AsyncOpenAI(api_key=api_key)
    ),
    tools=[order_tracking_process]
)