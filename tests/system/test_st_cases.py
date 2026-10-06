"""Style: identical to tests/unit — Flask test client + mock model, no live MySQL."""
from unittest.mock import patch, MagicMock


# ST-01: Mua hàng thành công — Login -> product -> cart -> checkout -> submit
@patch("controllers.checkout.OrderModel")
@patch("controllers.checkout.UserModel")
@patch("controllers.cart.ProductModel")
def test_st01_purchase_success(MockProd, MockUser, MockOrder, client):
    # login as user via session (bypass real login)
    with client.session_transaction() as sess:
        sess.update(user_id=2, user_fullname="Test User", user_email="user@example.com", user_role="user")
    MockProd.find_by_id.return_value = {"id": 1, "name": "Laptop A", "price": 20000000, "image": "a.jpg", "is_active": 1, "stock": 20}
    MockUser.find_by_id.return_value = {"id": 2, "fullname": "Test User", "email": "user@example.com", "phone": "0912345678", "address": "123 St"}
    MockOrder.create_order.return_value = 101
    MockOrder.find_by_id.return_value = {"id": 101, "user_id": 2, "total_amount": 20000000, "status": "pending", "receiver_name": "Test User", "receiver_phone": "0912345678", "receiver_address": "123 St"}

    # 1) add to cart
    resp = client.post("/cart/add", data={"product_id": "1", "quantity": "1"}, follow_redirects=False)
    assert resp.status_code == 302

    # 2) checkout
    resp = client.post("/checkout/", data={
        "receiver_name": "Test User", "receiver_phone": "0912345678",
        "receiver_address": "123 St", "payment_method": "cod", "note": ""
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert "success/101" in resp.location

    # 3) cart cleared
    with client.session_transaction() as sess:
        assert "cart" not in sess


# ST-02: Checkout khi hết hàng
@patch("controllers.checkout.OrderModel")
@patch("controllers.checkout.UserModel")
def test_st02_out_of_stock(MockUser, MockOrder, client):
    with client.session_transaction() as sess:
        sess.update(user_id=2, user_fullname="Test User", user_email="user@example.com", user_role="user")
        sess["cart"] = {"1": {"id": 1, "name": "Laptop A", "price": 20000000, "image": "a.jpg", "quantity": 5}}
    MockUser.find_by_id.return_value = {"id": 2, "fullname": "Test User", "email": "user@example.com", "phone": "0912345678", "address": "123 St"}
    MockOrder.create_order.return_value = {"error": "Sản phẩm Laptop A không đủ tồn kho (Còn 1)."}
    resp = client.post("/checkout/", data={
        "receiver_name": "Test User", "receiver_phone": "0912345678",
        "receiver_address": "123 St", "payment_method": "cod", "note": ""
    }, follow_redirects=True)
    assert "không đủ tồn kho" in resp.get_data(as_text=True)
    with client.session_transaction() as sess:
        assert "1" in sess.get("cart", {})


# ST-03: Admin xử lý order — pending -> processing -> shipping -> delivered
@patch("models.order.get_db")
def test_st03_order_state_machine(mock_get_db):
    from models.order import OrderModel

    def _set_status(status):
        cur = MagicMock()
        cur.__enter__ = MagicMock(return_value=cur)
        cur.__exit__ = MagicMock(return_value=False)
        cur.fetchone.return_value = {"status": status}
        cur.fetchall.return_value = []
        cur.execute = MagicMock()
        db = MagicMock()
        db.cursor.return_value = cur
        db.commit = MagicMock()
        db.rollback = MagicMock()
        mock_get_db.return_value = db

    _set_status("pending")
    ok, _ = OrderModel.update_status(1, "processing")
    assert ok is True
    _set_status("processing")
    ok, _ = OrderModel.update_status(1, "shipping")
    assert ok is True
    _set_status("shipping")
    ok, _ = OrderModel.update_status(1, "delivered")
    assert ok is True


# ST-04: Admin hủy order hoàn kho
@patch("models.order.get_db")
def test_st04_cancel_restock(mock_get_db):
    from models.order import OrderModel
    cur = MagicMock()
    cur.__enter__ = MagicMock(return_value=cur)
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchone.return_value = {"status": "pending"}
    cur.fetchall.return_value = [{"product_id": 1, "quantity": 2}]
    cur.execute = MagicMock()
    db = MagicMock()
    db.cursor.return_value = cur
    db.commit = MagicMock()
    db.rollback = MagicMock()
    mock_get_db.return_value = db
    ok, _ = OrderModel.update_status(1, "cancelled")
    assert ok is True


# ST-05: Admin nhập kho
@patch("models.inventory.get_db")
def test_st05_inventory_import(mock_get_db):
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
    assert InventoryModel.import_stock(1, 1, 10, "Test import", 1) is True


# ST-06: User truy cập admin — bị chặn
def test_st06_user_forbidden_admin(client):
    with client.session_transaction() as sess:
        sess.update(user_id=2, user_fullname="Test User", user_email="user@example.com", user_role="user")
    resp = client.get("/admin/", follow_redirects=False)
    assert resp.status_code == 302


# ST-07: User xem order của mình
@patch("controllers.orders.OrderModel")
def test_st07_view_own_orders(MockOrder, client):
    with client.session_transaction() as sess:
        sess.update(user_id=2, user_fullname="Test User", user_email="user@example.com", user_role="user")
    MockOrder.get_by_user.return_value = [{"id": 10, "user_id": 2, "total_amount": 20000000, "status": "pending"}]
    resp = client.get("/orders/")
    assert resp.status_code == 200


# ST-08: User không xem order của người khác
@patch("controllers.orders.OrderModel")
def test_st08_no_access_other_orders(MockOrder, client):
    with client.session_transaction() as sess:
        sess.update(user_id=2, user_fullname="Test User", user_email="user@example.com", user_role="user")
    MockOrder.find_by_id.return_value = None
    resp = client.get("/orders/detail/999", follow_redirects=False)
    assert resp.status_code in (302, 404)
