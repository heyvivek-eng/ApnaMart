from collections import Counter

from sqlalchemy import func, select

from app.main import app
from app.models import Product
from scripts.seed_demo import CATALOGS, IMAGE_DIRECTORY, PLACEHOLDER_IMAGE, generate_demo_products, seed_products


def seed_product(client, name: str = "Cotton Kurta", sku: str = "KURTA-1", stock: int = 4) -> None:
    db = app.state.test_session_factory()
    try:
        db.add(
            Product(
                name=name,
                description="Hand-finished everyday cotton kurta.",
                category="Clothing",
                sku=sku,
                price_paise=79900,
                stock=stock,
                image_url="",
            )
        )
        db.commit()
    finally:
        db.close()


def register_and_login(client, email="buyer@example.com"):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Test Buyer", "password": "A-strong-passphrase-44"},
    )
    assert response.status_code == 201
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "A-strong-passphrase-44"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_search_returns_database_products(client):
    seed_product(client)
    response = client.get("/api/v1/products", params={"q": "kurta"})
    assert response.status_code == 200
    assert [product["sku"] for product in response.json()] == ["KURTA-1"]


def test_demo_catalog_has_requested_distribution_unique_skus_and_descriptions():
    products = generate_demo_products()
    assert len(products) == 1000
    assert len({product.sku for product in products}) == len(products)
    assert all(product.name and len(product.description) > 50 for product in products)
    assert all(product.price_paise > 0 and product.stock > 0 for product in products)
    assert all(product.image_url.startswith(f"{IMAGE_DIRECTORY}/") for product in products)
    assert len({product.image_url for product in products}) >= 25
    assert all(
        len({product.image_url for product in products if product.category == catalog.category}) >= 3
        for catalog in CATALOGS
    )

    expected_counts = {
        catalog.category: len(catalog.families) * 10
        for catalog in CATALOGS
    }
    assert Counter(product.category for product in products) == expected_counts


def test_demo_seeder_is_idempotent_and_preserves_existing_products(client):
    seed_product(client, name="Existing product", sku="EXISTING-1")
    with app.state.test_session_factory() as db:
        first_inserted, first_existing = seed_products(db)
        db.commit()
        assert (first_inserted, first_existing) == (1000, 0)

        second_inserted, second_existing = seed_products(db)
        db.commit()
        assert (second_inserted, second_existing) == (0, 1000)
        assert db.scalar(select(func.count()).select_from(Product)) == 1001
        assert db.scalar(select(Product.id).where(Product.sku == "EXISTING-1")) is not None
        assert db.scalar(select(Product.image_url).where(Product.sku == "EXISTING-1")) != PLACEHOLDER_IMAGE
        first_demo = db.scalar(select(Product).where(Product.sku.like("DEMO-%")).order_by(Product.id))
        first_demo.image_url = PLACEHOLDER_IMAGE
        db.commit()

        inserted_again, existing_again = seed_products(db)
        db.commit()
        assert (inserted_again, existing_again) == (0, 1000)
        assert first_demo.image_url.startswith(f"{IMAGE_DIRECTORY}/")
        category_counts = dict(
            db.execute(
                select(Product.category, func.count())
                .where(Product.sku.like("DEMO-%"))
                .group_by(Product.category)
            ).all()
        )
        assert category_counts == {catalog.category: len(catalog.families) * 10 for catalog in CATALOGS}


def test_demo_seeder_pictures_original_products_without_changing_catalog_data(client):
    db = app.state.test_session_factory()
    try:
        originals = [
            Product(
                name="Everyday Cotton Kurta",
                category="Clothing",
                sku="DEMO-KURTA",
                price_paise=79900,
                stock=8,
                image_url="",
            ),
            Product(
                name="Steel Insulated Bottle",
                category="Home & Kitchen",
                sku="DEMO-BOTTLE",
                price_paise=49900,
                stock=12,
                image_url="",
            ),
            Product(
                name="Wireless Earbuds",
                category="Electronics",
                sku="DEMO-EARBUDS",
                price_paise=129900,
                stock=5,
                image_url="",
            ),
        ]
        db.add_all(originals)
        db.commit()
        before = {
            product.sku: (product.id, product.name, product.price_paise, product.stock)
            for product in originals
        }

        seed_products(db)
        db.commit()

        after = db.scalars(select(Product).where(Product.sku.in_(before))).all()
        assert len(after) == 3
        for product in after:
            assert (product.id, product.name, product.price_paise, product.stock) == before[product.sku]
            assert product.image_url.startswith(f"{IMAGE_DIRECTORY}/")
    finally:
        db.close()


def test_product_api_pagination_sort_category_and_detail(client):
    db = app.state.test_session_factory()
    try:
        db.add_all(
            [
                Product(
                    name=f"Catalog item {index}",
                    description="A useful demo item for endpoint pagination.",
                    category="Electronics & Accessories",
                    sku=f"PAGE-{index}",
                    price_paise=index * 100,
                    stock=10,
                    image_url=PLACEHOLDER_IMAGE,
                )
                for index in range(1, 5)
            ]
        )
        db.commit()
    finally:
        db.close()

    first_page = client.get(
        "/api/v1/products",
        params={"category": "Electronics & Accessories", "sort": "price_asc", "limit": 2, "offset": 0},
    )
    second_page = client.get(
        "/api/v1/products",
        params={"category": "Electronics & Accessories", "sort": "price_asc", "limit": 2, "offset": 2},
    )
    assert first_page.status_code == second_page.status_code == 200
    assert [product["sku"] for product in first_page.json()] == ["PAGE-1", "PAGE-2"]
    assert [product["sku"] for product in second_page.json()] == ["PAGE-3", "PAGE-4"]

    detail = client.get(f"/api/v1/products/{first_page.json()[0]['id']}")
    assert detail.status_code == 200
    assert detail.json()["sku"] == "PAGE-1"
    assert client.get("/api/v1/products/99999").status_code == 404


def test_cart_checkout_snapshots_price_and_marks_cod_unpaid(client):
    seed_product(client)
    headers = register_and_login(client)
    products = client.get("/api/v1/products").json()
    added = client.post(
        "/api/v1/cart/items",
        json={"product_id": products[0]["id"], "quantity": 2},
        headers=headers,
    )
    assert added.status_code == 200
    assert added.json()["total_paise"] == 159800

    placed = client.post("/api/v1/orders/checkout", json={"payment_method": "cod"}, headers=headers)
    assert placed.status_code == 201
    assert placed.json()["total_paise"] == 159800
    assert placed.json()["payment_status"] == "unpaid"
    assert placed.json()["items"][0]["product_name"] == "Cotton Kurta"
    assert client.get("/api/v1/cart", headers=headers).json()["items"] == []


def test_customer_cannot_read_another_customers_order(client):
    seed_product(client)
    first = register_and_login(client, "first@example.com")
    product_id = client.get("/api/v1/products").json()[0]["id"]
    client.post("/api/v1/cart/items", json={"product_id": product_id, "quantity": 1}, headers=first)
    order = client.post("/api/v1/orders/checkout", json={"payment_method": "cod"}, headers=first).json()
    second = register_and_login(client, "second@example.com")
    response = client.get(f"/api/v1/orders/{order['id']}", headers=second)
    assert response.status_code == 404
