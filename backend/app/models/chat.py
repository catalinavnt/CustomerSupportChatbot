from pydantic import BaseModel, Field

class Message(BaseModel):
    sender: str
    text:str

class ChatRequest(BaseModel):
    message: str = Field(
        min_lenght=1,
        max_lenght=1000
    )
    
    conversation_id: int | None = Field(
        default=None,
        gt=0
    )

    guest_session_id: str | None = Field(
        default=None,
        max_length=36
    )


class ChatResponse(BaseModel):
    response: str
    sources: list[str]
    conversation_id: int | None