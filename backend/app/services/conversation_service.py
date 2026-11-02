from sqlalchemy.orm import Session

from app.models.database_models import Conversation, Message


def get_or_create_conversation(
    db: Session,
    conversation_id: int | None,
    user_id: int
) -> Conversation:

    if conversation_id is not None:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            .first()
        )

        if conversation:
            return conversation

    conversation = Conversation(
        user_id=user_id
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def add_message(
    db: Session,
    conversation_id: int,
    sender: str,
    text: str
) -> Message:

    message = Message(
        conversation_id=conversation_id,
        sender=sender,
        text=text
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_history(
    db: Session,
    conversation_id: int
) -> list[Message]:

    return (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.created_at)
        .all()
    )

def get_or_create_guest_conversation(
        db: Session,
        guest_session_id: str
) -> Conversation:

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.guest_session_id == guest_session_id,
            Conversation.user_id.is_(None)
        )
        .first()
    )

    if conversation:
        return conversation

    conversation = Conversation(
        user_id=None,
        guest_session_id=guest_session_id
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation

def claim_guest_conversation(
    db: Session,
    guest_session_id: str | None,
    user_id: int
) -> Conversation | None:

    if not guest_session_id:
        return None

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.guest_session_id == guest_session_id,
            Conversation.user_id.is_(None)
        )
        .first()
    )

    if not conversation:
        return None

    conversation.user_id = user_id
    conversation.guest_session_id = None

    db.commit()
    db.refresh(conversation)

    return conversation