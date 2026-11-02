import re
from app.services.llm_service import generate_response

from sqlalchemy.orm import Session

from app.models.database_models import Order


def get_order(
    db: Session,
    order_id: int,
    user_id: int
) -> Order | None:
    return (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == user_id
        )
        .first()
    )


def generate_order_response(
    question: str,
    order_id: str,
    order: Order
) -> str:

    prompt = f"""
Answer the customer's question using only the order information below.

Order ID: {order_id}
Status: {order.status}
Carrier: {order.carrier}
Estimated delivery: {order.estimated_delivery}
Can be cancelled: {order.can_cancel}

Customer question:
{question}

Answer only what is relevant to the question.
Do not invent information.
Keep the answer concise and natural.
"""

    return generate_response(prompt)


def extract_order_id(
    message: str,
    history: list | None = None
) -> int | None:

    match = re.search(r"#?(\d{5})\b", message)

    if match:
        return int(match.group(1))

    if history:
        for item in reversed(history):
            match = re.search(
                r"#?(\d{5})\b",
                item.text
            )

            if match:
                return int(match.group(1))

    return None