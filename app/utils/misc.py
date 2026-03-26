import re

ORDER_ID_PATTERN = re.compile(r"\bORD-\d{4}\b")


def extract_order_id(text: str) -> str | None:
    match = ORDER_ID_PATTERN.search(text)
    return match.group() if match else None
