from unittest.mock import patch


class TestCheckoutRoutes:
    def test_checkout_page_requires_login(self, client):
        response = client.get('/checkout/')

        assert response.status_code == 302
        assert response.location.endswith('/login')

    def test_checkout_page_redirects_when_cart_empty(self, user_session):
        response = user_session.get('/checkout/', follow_redirects=True)

        assert response.status_code == 200
        assert 'Giỏ hàng trống.' in response.get_data(as_text=True)

    @patch('controllers.checkout.UserModel.find_by_id')
    def test_checkout_page_renders_form_with_cart(self, find_by_id, user_session):
        find_by_id.return_value = {
            'id': 2,
            'fullname': 'Test User',
            'email': 'user@example.com',
            'phone': '0912345678',
            'address': '123 Test St',
        }

        with user_session.session_transaction() as session:
            session['cart'] = {
                '1': {'id': 1, 'name': 'Laptop A', 'price': 20000000, 'image': 'a.jpg', 'quantity': 2}
            }

        response = user_session.get('/checkout/')

        assert response.status_code == 200
        data = response.get_data(as_text=True)
        assert 'Thanh toán' in data
        assert 'Laptop A' in data

    @patch('controllers.checkout.UserModel.find_by_id')
    @patch('controllers.checkout.OrderModel.create_order')
    def test_checkout_creates_order_and_clears_cart(self, create_order, find_by_id, user_session):
        find_by_id.return_value = {
            'id': 2,
            'fullname': 'Test User',
            'email': 'user@example.com',
            'phone': '0912345678',
            'address': '123 Test St',
        }
        create_order.return_value = 10

        with user_session.session_transaction() as session:
            session['cart'] = {
                '1': {'id': 1, 'name': 'Laptop A', 'price': 20000000, 'image': 'a.jpg', 'quantity': 2}
            }

        response = user_session.post(
            '/checkout/',
            data={
                'receiver_name': 'Test User',
                'receiver_phone': '0912345678',
                'receiver_address': '123 Test St',
                'payment_method': 'cod',
                'note': 'Please call before delivery',
            },
        )

        assert response.status_code == 302
        assert response.location.endswith('/checkout/success/10')
        with user_session.session_transaction() as session:
            assert 'cart' not in session
        create_order.assert_called_once()

    @patch('controllers.checkout.UserModel.find_by_id')
    @patch('controllers.checkout.OrderModel.create_order')
    def test_checkout_shows_error_when_order_creation_fails(self, create_order, find_by_id, user_session):
        find_by_id.return_value = {
            'id': 2,
            'fullname': 'Test User',
            'email': 'user@example.com',
            'phone': '0912345678',
            'address': '123 Test St',
        }
        create_order.return_value = {'error': 'Sản phẩm Laptop A không đủ tồn kho (Còn 1).'}

        with user_session.session_transaction() as session:
            session['cart'] = {
                '1': {'id': 1, 'name': 'Laptop A', 'price': 20000000, 'image': 'a.jpg', 'quantity': 5}
            }

        response = user_session.post(
            '/checkout/',
            data={
                'receiver_name': 'Test User',
                'receiver_phone': '0912345678',
                'receiver_address': '123 Test St',
                'payment_method': 'cod',
                'note': '',
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert 'không đủ tồn kho' in response.get_data(as_text=True)
        with user_session.session_transaction() as session:
            assert '1' in session['cart']

    @patch('controllers.checkout.OrderModel.find_by_id')
    def test_checkout_success_page_shows_order(self, find_by_id, user_session):
        find_by_id.return_value = {
            'id': 10,
            'user_id': 2,
            'total_amount': 40000000,
            'status': 'pending',
            'receiver_name': 'Test User',
            'receiver_phone': '0912345678',
            'receiver_address': '123 Test St',
        }

        response = user_session.get('/checkout/success/10')

        assert response.status_code == 200
        data = response.get_data(as_text=True)
        assert 'Đặt hàng thành công' in data

    @patch('controllers.checkout.OrderModel.find_by_id')
    def test_checkout_success_redirects_if_order_not_found(self, find_by_id, user_session):
        find_by_id.return_value = None

        response = user_session.get('/checkout/success/999')

        assert response.status_code == 302
        assert response.location.endswith('/')
