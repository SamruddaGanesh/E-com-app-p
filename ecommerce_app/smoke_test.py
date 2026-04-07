from uuid import uuid4

from app import app, db, init_db, Product, User, Order


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with app.app_context():
        init_db()

    client = app.test_client()

    username = f"user_{uuid4().hex[:8]}"
    password = "testpass123"

    register_resp = client.post(
        "/register",
        data={"username": username, "password": password},
        follow_redirects=True,
    )
    assert_true(register_resp.status_code == 200, "Registration request failed")

    login_resp = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )
    assert_true(login_resp.status_code == 200, "User login failed")

    with app.app_context():
        product = Product.query.filter(Product.stock > 0).first()
        assert_true(product is not None, "No product with stock found")
        product_id = product.id
        stock_before_order = product.stock

    add_cart_resp = client.post(
        f"/add-to-cart/{product_id}",
        data={"quantity": "1"},
        follow_redirects=True,
    )
    assert_true(add_cart_resp.status_code == 200, "Add to cart failed")

    order_resp = client.post(
        "/place-order",
        data={"address": "221B Baker Street"},
        follow_redirects=True,
    )
    assert_true(order_resp.status_code == 200, "Place order failed")

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        assert_true(user is not None, "User missing after registration")

        latest_order = (
            Order.query.filter_by(user_id=user.id)
            .order_by(Order.created_at.desc())
            .first()
        )
        assert_true(latest_order is not None, "Order was not created")
        assert_true(latest_order.address == "221B Baker Street", "Order address mismatch")

        updated_product = Product.query.get(product_id)
        assert_true(updated_product is not None, "Ordered product missing")
        assert_true(
            updated_product.stock == stock_before_order - 1,
            "Product stock was not reduced after order",
        )

    client.get("/logout", follow_redirects=True)

    admin_login_resp = client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )
    assert_true(admin_login_resp.status_code == 200, "Admin login failed")

    admin_product_name = f"AdminItem_{uuid4().hex[:6]}"
    add_product_resp = client.post(
        "/admin/products",
        data={"name": admin_product_name, "price": "999.00", "stock": "5"},
        follow_redirects=True,
    )
    assert_true(add_product_resp.status_code == 200, "Admin add product failed")

    with app.app_context():
        admin_product = Product.query.filter_by(name=admin_product_name).first()
        assert_true(admin_product is not None, "Admin-added product not found")
        admin_product_id = admin_product.id

    update_price_resp = client.post(
        f"/admin/update-price/{admin_product_id}",
        data={"price": "1099.00"},
        follow_redirects=True,
    )
    assert_true(update_price_resp.status_code == 200, "Admin update price failed")

    with app.app_context():
        admin_product = Product.query.get(admin_product_id)
        assert_true(admin_product is not None, "Admin product missing after price update")
        assert_true(abs(admin_product.price - 1099.00) < 0.0001, "Price did not update")

    delete_product_resp = client.post(
        f"/admin/delete-product/{admin_product_id}",
        follow_redirects=True,
    )
    assert_true(delete_product_resp.status_code == 200, "Admin delete product failed")

    with app.app_context():
        deleted = Product.query.get(admin_product_id)
        assert_true(deleted is None, "Admin product was not deleted")

    print("SMOKE TEST PASSED: user flow and admin flow are working.")


if __name__ == "__main__":
    main()
