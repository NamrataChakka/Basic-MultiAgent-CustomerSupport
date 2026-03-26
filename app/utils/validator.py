import re
from datetime import datetime, timedelta

ORDER_NUMBER = r"^ORD-\d{4}$"

def is_valid_order_id(order_id: str) -> bool:
    return bool(re.match(ORDER_NUMBER, order_id))

def is_within_24_hours(order_time: str) -> bool:
    return datetime.now() < datetime.fromisoformat(order_time) + timedelta(hours=24)
