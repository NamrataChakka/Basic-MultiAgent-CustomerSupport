import json
import os
import logging
from app.utils.validator import is_valid_order_id, is_within_24_hours
from agents import function_tool
from openai import OpenAI


logger = logging.getLogger(__name__)

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    product_vector_store_id = os.getenv("PRODUCT_VECTOR_STORE_ID")
    logger.info("OpenAI client & vector store initialized successfully.")

except Exception as e:
    logger.error(f"Failed to initialize OpenAI client or vector store. {e}")


@function_tool
def order_cancellation_process(order_id: str) -> str:
    """
    Business logic to cancel an order. Fetches from orders.json.
    """
    try:
        with open("app/dataset/orders.json", "r") as f:
            orders = json.load(f)

        order = orders.get(order_id)
        if not order:
            return f"Order {order_id} not found."

        if not is_valid_order_id(order_id):
            return f"Order {order_id} not valid. Order format: ORD-XXXX"

        if order["status"] == "cancelled":
            return f"Order {order_id} is already cancelled."

        if not is_within_24_hours(order["created_at"]):
            return f"Order {order_id} cannot be cancelled because it was placed more than 24 hours ago."

        order["status"] = "cancelled"
        order["refunded"] = True
        with open("dataset/orders.json", "w") as f:
            json.dump(orders, f, indent=4)
        return f"Order {order_id} has been successfully cancelled. A refund has been initiated."

    except Exception as e:
        return f"Error processing cancellation: {str(e)}"

@function_tool
def order_tracking_process(order_id: str) -> str:
    """
    Look up the status of an order in the database.
    Args:
        order_id: The full order ID string, e.g., 'ORD-1234'.
    """
    try:
        with open("app/dataset/orders.json", "r") as f:
            orders = json.load(f)

        order = orders.get(order_id)
        if not order:
            return f"Order {order_id} not found."

        if not is_valid_order_id(order_id):
            return f"Order {order_id} not valid. Order format: ORD-XXXX"
        logger.info(f"Summarize to the user: Tracking status of order: {order_id}. Status: {order['status']}. Delivery date: {order['delivery_date']}")
        return f"Summarize to the user: Tracking status of order: {order_id}. Status: {order['status']}. Delivery date: {order['delivery_date']}"

    except Exception as e:
        return f"Error processing cancellation: {str(e)}"


@function_tool()
def lookup_product_in_vector_store(product_name: str) -> dict:
    """Search for product information in the vector store."""
    logger.info(f"Searching vector store for product: {product_name}")
    try:
        results = client.vector_stores.search(
            vector_store_id=product_vector_store_id,
            query=product_name,
            max_num_results=1
        )
        logger.info(f"Product lookup results: {results}")
        return results
    except Exception as e:
        logger.error(f"Error looking up product '{product_name}': {e}")
        return {"error": str(e)}


def upload_to_file_api(client, file_path: str) -> str:
    with open(file_path, "rb") as file_content:
            result = client.files.create(
                file=file_content,
                purpose="assistants"
            )
    return result.id

def create_vector_store(file_path):
    file_id = upload_to_file_api(client, file_path=file_path)
    vector_store = client.vector_stores.create(
        name="product_information"
    )
    client.vector_stores.files.create(
        vector_store_id=vector_store.id,
        file_id=file_id
    )

    with open(".env", "a") as f:
        f.write(f"PRODUCT_VECTOR_STORE_ID={vector_store.id}\n")
