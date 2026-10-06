"""Integration-style tests (mocked DB) — map IT-AUTH/PROD/CART/ORD/ADM/INV."""
from unittest.mock import patch, MagicMock


# IT-AUTH-01: tạo user mới
@patch("controllers.auth.UserModel")
def test_it_auth_create_user(MockUser, client):
    MockUser.find_by_email.return_value = None  # chưa tồn tại
    MockUser.create.return_value = 10
    resp = client.post("/register", data={
        "fullname": "Nguyen Van A",
        "email": "newuser@example.com",
        "phone": "0912345678",
        "password": "secret1",
        "password_confirm": "secret1",
    }, follow_redirects=False)
    assert resp.status_code in (302, 200)
    MockUser.create.assert_called_once()


# IT-AUTH-02: login hợp lệ
@patch("controllers.auth.UserModel")
def test_it_auth_login_valid(MockUser, client):
    from werkzeug.security import generate_password_hash
    MockUser.find_by_email.return_value = {
        "id": 2, "fullname": "Test User", "email": "user@example.com",
        "password": generate_password_hash("secret1"), "is_locked": 0, "role": "user"
    }
    resp = client.post("/login", data={"email": "user@example.com", "password": "secret1"}, follow_redirects=False)
    assert resp.status_code == 302


# IT-AUTH-03: từ chối account locked
@patch("controllers.auth.UserModel")
def test_it_auth_locked_rejected(MockUser, client):
    from werkzeug.security import generate_password_hash
    MockUser.find_by_email.return_value = {
        "id": 3, "fullname": "Locked", "email": "locked@example.com",
        "password": generate_password_hash("secret1"), "is_locked": 1, "role": "user"
    }
    resp = client.post("/login", data={"email": "locked@example.com", "password": "secret1"}, follow_redirects=True)
    assert "bị khóa" in resp.get_data(as_text=True)


# IT-PROD-01: lọc active product
@patch("controllers.products.ProductModel")
def test_it_prod_filter_active(MockProd, client):
    MockProd.get_all.return_value = [
        {"id": 1, "name": "ASUS A", "brand": "ASUS", "is_active": 1, "stock": 10, "price": 20000000, "cpu": "i5", "ram": "8GB", "storage": "512GB", "image": "a.jpg"},
    ]
    MockProd.get_all_brands.return_value = ["ASUS"]
    resp = client.get("/products?brand=ASUS")
    assert resp.status_code == 200
    MockProd.get_all.assert_called_once()


# IT-CART-01: thêm product vào cart
@patch("controllers.cart.ProductModel")
def test_it_cart_add(MockProd, client):
    MockProd.find_by_id.return_value = {"id": 1, "name": "Laptop A", "price": 20000000, "image": "a.jpg", "is_active": 1, "stock": 20}
    resp = client.post("/cart/add", data={"product_id": "1", "quantity": "2"}, follow_redirects=False)
    assert resp.status_code == 302
    with client.session_transaction() as sess:
        assert sess.get("cart") is not None


# IT-ORD-01: tạo order đủ stock
@patch("controllers.checkout.OrderModel")
@patch("controllers.checkout.UserModel")
def test_it_ord_create_success(MockUser, MockOrder, user_session):
    MockUser.find_by_id.return_value = {"id": 2, "fullname": "Test User", "email": "u@e.com", "phone": "0912345678", "address": "123 St"}
    MockOrder.create_order.return_value = 101
    with user_session.session_transaction() as sess:
        sess["cart"] = {"1": {"id": 1, "name": "Laptop A", "price": 20000000, "image": "a.jpg", "quantity": 1}}
    resp = user_session.post("/checkout/", data={
        "receiver_name": "Test User", "receiver_phone": "0912345678",
        "receiver_address": "123 St", "payment_method": "cod", "note": ""
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert "success/101" in resp.location


# IT-ORD-02: rollback khi lỗi detail
@patch("controllers.checkout.OrderModel")
@patch("controllers.checkout.UserModel")
def test_it_ord_rollback_on_error(MockUser, MockOrder, user_session):
    MockUser.find_by_id.return_value = {"id": 2, "fullname": "Test User", "email": "u@e.com", "phone": "0912345678", "address": "123 St"}
    MockOrder.create_order.return_value = {"error": "Sản phẩm Laptop A không đủ tồn kho (Còn 1)."}
    with user_session.session_transaction() as sess:
        sess["cart"] = {"1": {"id": 1, "name": "Laptop A", "price": 20000000, "image": "a.jpg", "quantity": 5}}
    resp = user_session.post("/checkout/", data={
        "receiver_name": "Test User", "receiver_phone": "0912345678",
        "receiver_address": "123 St", "payment_method": "cod", "note": ""
    }, follow_redirects=True)
    assert "không đủ tồn kho" in resp.get_data(as_text=True)


# IT-ORD-03: hủy order hoàn stock (mock model trực tiếp)
@patch("models.order.get_db")
def test_it_ord_cancel_restock(mock_get_db):
    from models.order import OrderModel
    cur = MagicMock()
    cur.__enter__ = MagicMock(return_value=cur)
    cur.__exit__ = MagicMock(return_value=False)
    # lần 1: SELECT status
    cur.fetchone.return_value = {"status": "pending"}
    cur.fetchall.return_value = [{"product_id": 1, "quantity": 2}]
    cur.execute = MagicMock()
    db = MagicMock()
    db.cursor.return_value = cur
    db.commit = MagicMock()
    db.rollback = MagicMock()
    mock_get_db.return_value = db
    ok, msg = OrderModel.update_status(1, "cancelled")
    assert ok is True


# IT-ADM-01: chặn user vào admin
def test_it_adm_forbidden_for_user(user_session):
    resp = user_session.get("/admin/", follow_redirects=False)
    assert resp.status_code == 302


# IT-INV-01: nhập kho
@patch("models.inventory.get_db")
def test_it_inv_import(mock_get_db):
    from models.inventory import InventoryModel
    cur = MagicMock()
    cur.__enter__ = MagicMock(return_value=cur)
    cur.__exit__ = MagicMock(return_value=False)
    cur.execute = MagicMock()
    db = MagicMock()
    db.cursor.return_value = cur
    db.commit = MagicMock()
    db.rollback = MagicMock()
    mock_get_db.return_value = db
    ok = InventoryModel.import_stock(1, 1, 10, "Test import", 1)
    assert ok is True
