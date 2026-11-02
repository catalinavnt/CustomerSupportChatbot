import os

from fastapi import FastAPI, Depends, HTTPException
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.chat import ChatRequest, ChatResponse
from app.services.rag_service import generate_rag_response
from app.services.order_service import generate_order_response, get_order, extract_order_id
from app.services.intent_classifier import classify_intent 

from app.services.conversation_service import (
    add_message,
    get_history,
    get_or_create_conversation,
    get_or_create_guest_conversation,
    claim_guest_conversation
)

from app.database import Base, engine, SessionLocal
from app.models.database_models import User, Conversation, Message
from sqlalchemy.orm import Session

from app.models.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse
)
from app.services.auth_service import (
    create_access_token,
    hash_password,
    verify_password,
    decode_access_token
)

load_dotenv()

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:4200"
)

app = FastAPI(
    title="AI Customer Support API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


security = HTTPBearer(auto_error=False)

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> User:

    user_id = decode_access_token(credentials.credentials)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db)
) -> User | None:

    if credentials is None:
        return None

    user_id = decode_access_token(credentials.credentials)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    return user



@app.get("/")
def root():
    return {
        "status": "Customer Support API is running"
    }

@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user)
):
    conversation = None
    history = []

    if current_user:
        conversation = get_or_create_conversation(
            db,
            request.conversation_id,
            current_user.id
        )

    elif request.guest_session_id:
        conversation = get_or_create_guest_conversation(
            db,
            request.guest_session_id
        )

    if conversation:
        history = get_history(
            db,
            conversation.id
        )

    classification = classify_intent(
        request.message,
        history
    )

    intent = classification["intent"]

    if conversation:
        add_message(
            db,
            conversation.id,
            "user",
            request.message
        )

    if intent == "order_status":
        if not current_user:
            response_text = "Please log in to check your order."
            sources = []
        else:
            order_id = extract_order_id(
                request.message,
                history
            )

            if not order_id:
                response_text = "Please provide your order number."
                sources = []
            else:
                order = get_order(
                    db,
                    order_id,
                    current_user.id
                )

                if not order:
                    response_text = "I couldn't find that order."
                    sources = []
                else:
                    response_text = generate_order_response(
                    request.message,
                    order_id,
                    order
                )

                sources = []

    else:
        result = generate_rag_response(
            request.message,
            history
        )

        response_text = result["response"]
        sources = result["sources"]

    if conversation:
        add_message(
            db,
            conversation.id,
            "bot",
            response_text
        )

    return ChatResponse(
        response=response_text,
        sources=sources,
        conversation_id=conversation.id if conversation else None
    )

@app.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )
    
    messages = get_history(
        db,
        conversation.id
    )

    return [
        {
            "sender": message.sender,
            "text": message.text
        }
        for message in messages
    ]

@app.post("/auth/register", response_model=TokenResponse)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    user = User(
        email=request.email,
        password_hash=hash_password(request.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    conversation = claim_guest_conversation(
        db,
        request.guest_session_id,
        user.id
    )

    return TokenResponse(
        access_token=create_access_token(user.id),
        conversation_id=conversation.id if conversation else None
    )


@app.post("/auth/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user or not verify_password(
        request.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    conversation = claim_guest_conversation(
        db,
        request.guest_session_id,
        user.id
    )

    return TokenResponse(
        access_token=create_access_token(user.id),
        conversation_id=conversation.id if conversation else None
    )