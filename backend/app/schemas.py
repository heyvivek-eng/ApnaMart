from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=10, max_length=128)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    sku: str
    price_paise: int
    stock: int
    image_url: str
    model_config = ConfigDict(from_attributes=True)


class CartItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=50)


class CartLineResponse(BaseModel):
    product: ProductResponse
    quantity: int
    line_total_paise: int


class CartResponse(BaseModel):
    items: list[CartLineResponse]
    total_paise: int


class CheckoutRequest(BaseModel):
    payment_method: str = Field(pattern="^(cod)$")


class OrderItemResponse(BaseModel):
    product_name: str
    sku: str
    unit_price_paise: int
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    status: str
    payment_method: str
    payment_status: str
    total_paise: int
    items: list[OrderItemResponse]
    model_config = ConfigDict(from_attributes=True)
