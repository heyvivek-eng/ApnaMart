from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.dependencies import current_user, get_db
from app.models import CartItem, Order, OrderItem, Product, User, UserRole
from app.schemas import (
    CartItemRequest,
    CartLineResponse,
    CartResponse,
    CheckoutRequest,
    OrderResponse,
    ProductResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.security import create_access_token, hash_password, verify_password


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title="ApnaMart API",
    version="1.0.0",
    description="Initial marketplace API. API documentation is available at /docs.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        role=UserRole.customer,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists") from exc
    db.refresh(user)
    return user


@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    user = db.scalar(select(User).where(User.email == credentials.username.lower()))
    if user is None or not user.is_active or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user.id), "user": user}


@app.get("/api/v1/auth/me", response_model=UserResponse)
def me(user: User = Depends(current_user)) -> User:
    return user


@app.get("/api/v1/products", response_model=list[ProductResponse])
def list_products(
    q: str | None = Query(default=None, max_length=100),
    category: str | None = Query(default=None, max_length=100),
    sort: str = Query(default="newest", pattern="^(newest|price_asc|price_desc)$"),
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Product]:
    statement = select(Product).where(Product.is_active.is_(True))
    if q:
        statement = statement.where(Product.name.ilike(f"%{q.strip()}%"))
    if category:
        statement = statement.where(Product.category == category)
    if sort == "price_asc":
        statement = statement.order_by(Product.price_paise.asc(), Product.id.asc())
    elif sort == "price_desc":
        statement = statement.order_by(Product.price_paise.desc(), Product.id.asc())
    else:
        statement = statement.order_by(Product.created_at.desc(), Product.id.desc())
    return list(db.scalars(statement.offset(offset).limit(limit)).all())


@app.get("/api/v1/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)) -> Product:
    product = db.get(Product, product_id)
    if product is None or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def cart_snapshot(db: Session, user_id: int) -> CartResponse:
    rows = db.scalars(
        select(CartItem).options(joinedload(CartItem.product)).where(CartItem.user_id == user_id)
    ).all()
    items = [
        CartLineResponse(
            product=row.product,
            quantity=row.quantity,
            line_total_paise=row.product.price_paise * row.quantity,
        )
        for row in rows
    ]
    return CartResponse(items=items, total_paise=sum(item.line_total_paise for item in items))


@app.get("/api/v1/cart", response_model=CartResponse)
def get_cart(user: User = Depends(current_user), db: Session = Depends(get_db)) -> CartResponse:
    return cart_snapshot(db, user.id)


@app.post("/api/v1/cart/items", response_model=CartResponse)
def add_cart_item(
    payload: CartItemRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> CartResponse:
    product = db.get(Product, payload.product_id)
    if product is None or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    if payload.quantity > product.stock:
        raise HTTPException(status_code=409, detail="Requested quantity is not available")
    item = db.scalar(
        select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product.id)
    )
    next_quantity = payload.quantity + (item.quantity if item else 0)
    if next_quantity > product.stock:
        raise HTTPException(status_code=409, detail="Requested quantity exceeds available stock")
    if item:
        item.quantity = next_quantity
    else:
        db.add(CartItem(user_id=user.id, product_id=product.id, quantity=payload.quantity))
    db.commit()
    return cart_snapshot(db, user.id)


@app.put("/api/v1/cart/items/{product_id}", response_model=CartResponse)
def update_cart_item(
    product_id: int,
    payload: CartItemRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> CartResponse:
    if payload.product_id != product_id:
        raise HTTPException(status_code=422, detail="Product ID does not match request path")
    item = db.scalar(select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product_id))
    product = db.get(Product, product_id)
    if item is None or product is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if payload.quantity > product.stock:
        raise HTTPException(status_code=409, detail="Requested quantity is not available")
    item.quantity = payload.quantity
    db.commit()
    return cart_snapshot(db, user.id)


@app.delete("/api/v1/cart/items/{product_id}", response_model=CartResponse)
def remove_cart_item(
    product_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> CartResponse:
    item = db.scalar(select(CartItem).where(CartItem.user_id == user.id, CartItem.product_id == product_id))
    if item is not None:
        db.delete(item)
        db.commit()
    return cart_snapshot(db, user.id)


@app.post("/api/v1/orders/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    payload: CheckoutRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> Order:
    rows = db.scalars(
        select(CartItem).options(joinedload(CartItem.product)).where(CartItem.user_id == user.id)
    ).all()
    if not rows:
        raise HTTPException(status_code=400, detail="Your cart is empty")
    for row in rows:
        if not row.product.is_active or row.quantity > row.product.stock:
            raise HTTPException(status_code=409, detail=f"Stock changed for {row.product.name}")

    order = Order(
        customer_id=user.id,
        payment_method=payload.payment_method,
        payment_status="unpaid",
        total_paise=sum(row.product.price_paise * row.quantity for row in rows),
    )
    db.add(order)
    for row in rows:
        row.product.stock -= row.quantity
        order.items.append(
            OrderItem(
                product_id=row.product.id,
                product_name=row.product.name,
                sku=row.product.sku,
                unit_price_paise=row.product.price_paise,
                quantity=row.quantity,
            )
        )
        db.delete(row)
    db.commit()
    db.refresh(order)
    return order


@app.get("/api/v1/orders", response_model=list[OrderResponse])
def list_orders(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[Order]:
    return list(db.scalars(select(Order).where(Order.customer_id == user.id).order_by(Order.created_at.desc())).all())


@app.get("/api/v1/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Order:
    order = db.get(Order, order_id)
    if order is None or order.customer_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
