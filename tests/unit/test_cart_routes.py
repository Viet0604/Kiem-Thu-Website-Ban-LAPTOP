from unittest.mock import patch


class TestCartRoutes:
    def test_cart_page_renders_empty_cart(self, client):
        response = client.get('/cart/')

        assert response.status_code == 200
        assert 'Giỏ hàng' in response.get_data(as_text=True)

    def test_cart_page_calculates_total(self, client):
        with client.session_transaction() as session:
            session['cart'] = {
                '1': {'id': 1, 'name': 'Product A', 'price': 10000, 'image': 'a.jpg', 'quantity': 2},
                '2': {'id': 2, 'name': 'Product B', 'price': 15000, 'image': 'b.jpg', 'quantity': 3},
            }

        response = client.get('/cart/')

        assert response.status_code == 200
        data = response.get_data(as_text=True)
        assert 'Product A' in data
        assert 'Product B' in data

    @patch('controllers.cart.ProductModel.find_by_id')
    def test_add_to_cart_creates_new_cart_entry(self, find_by_id, client):
        find_by_id.return_value = {
            'id': 1,
            'name': 'Laptop A',
            'price': 20000000,
            'image': 'laptop_a.jpg',
            'stock': 10,
            'is_active': 1,
        }

        response = client.post(
            '/cart/add',
            data={'product_id': '1', 'quantity': '2'},
        )

        assert response.status_code == 302
        with client.session_transaction() as session:
            assert '1' in session['cart']
            assert session['cart']['1']['quantity'] == 2

    @patch('controllers.cart.ProductModel.find_by_id')
    def test_add_to_cart_increases_quantity_for_existing_item(self, find_by_id, client):
        find_by_id.return_value = {
            'id': 1,
            'name': 'Laptop A',
            'price': 20000000,
            'image': 'laptop_a.jpg',
            'stock': 10,
            'is_active': 1,
        }

        with client.session_transaction() as session:
            session['cart'] = {
                '1': {'id': 1, 'name': 'Laptop A', 'price': 20000000, 'image': 'laptop_a.jpg', 'quantity': 2}
            }

        response = client.post(
            '/cart/add',
            data={'product_id': '1', 'quantity': '3'},
            follow_redirects=True,
        )

        assert response.status_code == 200
        with client.session_transaction() as session:
            assert session['cart']['1']['quantity'] == 5

    @patch('models.product.ProductModel.get_latest')
    @patch('models.product.ProductModel.get_all_brands')
    @patch('controllers.cart.ProductModel.find_by_id')
    def test_add_to_cart_rejects_insufficient_stock(self, find_by_id, get_all_brands, get_latest, client):
        get_all_brands.return_value = []
        get_latest.return_value = []
        find_by_id.return_value = {
            'id': 1,
            'name': 'Laptop A',
            'price': 20000000,
            'image': 'laptop_a.jpg',
            'stock': 5,
            'is_active': 1,
        }

        response = client.post(
            '/cart/add',
            data={'product_id': '1', 'quantity': '10'},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert 'Số lượng tồn kho không đủ.' in response.get_data(as_text=True)

    @patch('models.product.ProductModel.get_latest')
    @patch('models.product.ProductModel.get_all_brands')
    @patch('controllers.cart.ProductModel.find_by_id')
    def test_add_to_cart_rejects_inactive_product(self, find_by_id, get_all_brands, get_latest, client):
        get_all_brands.return_value = []
        get_latest.return_value = []
        find_by_id.return_value = {
            'id': 1,
            'name': 'Laptop A',
            'price': 20000000,
            'image': 'laptop_a.jpg',
            'stock': 10,
            'is_active': 0,
        }

        response = client.post(
            '/cart/add',
            data={'product_id': '1', 'quantity': '2'},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert 'Sản phẩm không tồn tại.' in response.get_data(as_text=True)

    @patch('controllers.cart.ProductModel.find_by_id')
    def test_update_cart_changes_quantity(self, find_by_id, client):
        find_by_id.return_value = {
            'id': 1,
            'name': 'Laptop A',
            'price': 20000000,
            'image': 'laptop_a.jpg',
            'stock': 10,
            'is_active': 1,
        }

        with client.session_transaction() as session:
            session['cart'] = {
                '1': {'id': 1, 'name': 'Laptop A', 'price': 20000000, 'image': 'laptop_a.jpg', 'quantity': 2}
            }

        response = client.post(
            '/cart/update',
            data={'product_id': '1', 'quantity': '5'},
        )

        assert response.status_code == 302
        with client.session_transaction() as session:
            assert session['cart']['1']['quantity'] == 5

    @patch('controllers.cart.ProductModel.find_by_id')
    def test_update_cart_removes_item_when_quantity_zero(self, find_by_id, client):
        find_by_id.return_value = {
            'id': 1,
            'name': 'Laptop A',
            'price': 20000000,
            'image': 'laptop_a.jpg',
            'stock': 10,
            'is_active': 1,
        }

        with client.session_transaction() as session:
            session['cart'] = {
                '1': {'id': 1, 'name': 'Laptop A', 'price': 20000000, 'image': 'laptop_a.jpg', 'quantity': 2}
            }

        response = client.post(
            '/cart/update',
            data={'product_id': '1', 'quantity': '0'},
        )

        assert response.status_code == 302
        with client.session_transaction() as session:
            assert '1' not in session['cart']

    def test_remove_from_cart_deletes_item(self, client):
        with client.session_transaction() as session:
            session['cart'] = {
                '1': {'id': 1, 'name': 'Laptop A', 'price': 20000000, 'image': 'laptop_a.jpg', 'quantity': 2}
            }

        response = client.get('/cart/remove/1')

        assert response.status_code == 302
        with client.session_transaction() as session:
            assert '1' not in session['cart']
