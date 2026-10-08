from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# --- Auth Schemas ---
class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty or whitespace only")
        return cleaned


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Product Schemas ---
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    price: Decimal
    image_url: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Cart Schemas ---
class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=99)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1, le=99)


class CartItemResponse(BaseModel):
    product_id: int
    name: str
    price: Decimal
    quantity: int
    line_total: Decimal
    image_url: str | None = None


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    grand_total: Decimal
    item_count: int


# --- Order Schemas ---
class OrderItemResponse(BaseModel):
    id: int
    product_name: str
    price: Decimal
    quantity: int
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    grand_total: Decimal
    email_status: str
    created_at: datetime
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
