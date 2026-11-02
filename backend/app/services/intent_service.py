def detect_intent(message: str, history: list | None = None) -> str:
    text = message.lower().strip()

    order_keywords = [
        "order",
        "tracking",
        "where is my order",
        "delivery status"
    ]

    if any(keyword in text for keyword in order_keywords):
        return "order_status"

    # Detect messages such as "#12345" or "12345"
    import re
    if re.fullmatch(r"#?\d{5}", text.strip()):
        return "order_status"

    if history:
        recent_text = " ".join(
            item.text.lower()
            for item in history[-4:]
        )

        if "order" in recent_text or "tracking" in recent_text:
            return "order_status"

    return "knowledge"