from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User's email address", examples=["user@example.com"])
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username (3-50 characters)",
        examples=["johndoe", "user123"]
    )

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            raise ValueError(
                'Username must start with a letter and contain only letters, numbers, and underscores'
            )

        inappropriate_words = ['admin', 'root', 'system']
        if v.lower() in inappropriate_words:
            raise ValueError(f'Username "{v}" is reserved')

        return v.lower()


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User password (8-100 characters)",
        examples=["SecurePass123!"]
    )


    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')

        weak_passwords = ['password123', '12345678', 'qwerty123']
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common, please choose a stronger one')

        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="New email address (optional)")
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="New username (optional)"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=100,
        description="New password (optional)"
    )

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            raise ValueError(
                'Username must start with a letter and contain only letters, numbers, and underscores'
            )

        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')

        return v


class UserResponse(UserBase):
    id: int = Field(..., description="User's unique identifier")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_superuser: bool = Field(..., description="Whether user has admin privileges")
    created_at: datetime = Field(..., description="When the user account was created")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "john.doe@example.com",
                "username": "johndoe",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2024-01-15T10:30:00"
            }
        }
    }


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    token_type: str = Field(default="bearer", description="Token type (always 'bearer' for JWT)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ"
                                "zdWIiOiJqb2huZG9lIiwiZXhwIjoxNjE2MjM5MDIyfQ...",
                "token_type": "bearer"
            }
        }
    }


class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="Username extracted from token")
    exp: Optional[datetime] = Field(None, description="Token expiration time")


class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class PasswordChange(BaseModel):
    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="New password"
    )
    confirm_password: str = Field(..., description="Confirm new password")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v
