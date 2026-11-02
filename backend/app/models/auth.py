from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr

    password: str = Field(min_length=8)

    guest_session_id: str | None = Field(
        default=None,
        max_length=36
    )

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError(
                "Password must be at most 72 bytes."
            )

        return password


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    guest_session_id: str | None = Field(
        default=None,
        max_length=36
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    conversation_id: int | None = None