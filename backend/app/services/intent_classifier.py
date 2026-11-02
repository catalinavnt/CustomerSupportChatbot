import json

from app.services.llm_service import generate_response


ALLOWED_INTENTS = {
    "knowledge",
    "order_status"
}


CLASSIFIER_SYSTEM_PROMPT = """
You are an intent classification system for an online store customer support chatbot.

Classify the customer's current message into exactly one of these intents:

- knowledge:
  Questions about products, returns, shipping policies, warranty,
  store information, prices, or other knowledge-base information.

- order_status:
  Questions about an existing order, package tracking, delivery status,
  carrier, estimated delivery, or follow-up questions about an order.

Return ONLY valid JSON in exactly this format:

{
  "intent": "knowledge"
}

or:

{
  "intent": "order_status"
}

Do not answer the customer's question.
Do not include markdown, explanations, or additional text.
"""


def classify_intent(
    message: str,
    history: list | None = None
) -> dict:

    history_text = ""

    if history:
        recent_messages = history[-6:]

        history_text = "\n".join(
            f"{item.sender}: {item.text}"
            for item in recent_messages
        )

    prompt = f"""
Conversation history:
{history_text if history_text else "No previous conversation."}

Current customer message:
{message}
"""

    raw_response = generate_response(
        prompt,
        system_prompt=CLASSIFIER_SYSTEM_PROMPT
    )

    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError:
        return {
            "intent": "knowledge"
        }

    intent = result.get("intent")

    if intent not in ALLOWED_INTENTS:
        intent = "knowledge"

    return {
        "intent": intent
    }