from unittest.mock import patch

from werkzeug.security import generate_password_hash


class TestAuthRoutes:
    def test_login_page_renders(self, client):
        response = client.get('/login')

        assert response.status_code == 200
        assert 'Đăng nhập' in response.get_data(as_text=True)

    @patch('controllers.auth.UserModel.find_by_email', return_value=None)
    def test_login_rejects_unknown_email(self, find_by_email, client):
        response = client.post(
            '/login',
            data={'email': 'missing@example.com', 'password': 'secret123'},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert 'Email hoặc mật khẩu không chính xác.' in response.get_data(as_text=True)
        find_by_email.assert_called_once_with('missing@example.com')

    def test_login_rejects_missing_credentials(self, client):
        response = client.post(
            '/login',
            data={'email': '', 'password': ''},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert 'Vui lòng nhập email và mật khẩu.' in response.get_data(as_text=True)

    @patch('controllers.auth.UserModel.find_by_email')
    def test_login_rejects_locked_account(self, find_by_email, client):
        find_by_email.return_value = {
            'id': 2,
            'fullname': 'Locked User',
            'email': 'locked@example.com',
            'password': generate_password_hash('secret123'),
            'role': 'user',
            'is_locked': 1,
        }

        response = client.post(
            '/login',
            data={'email': 'locked@example.com', 'password': 'secret123'},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert 'Tài khoản của bạn đã bị khóa.' in response.get_data(as_text=True)

    @patch('controllers.auth.UserModel.find_by_email')
    def test_login_stores_user_session_and_redirects_user(self, find_by_email, client):
        find_by_email.return_value = {
            'id': 2,
            'fullname': 'Normal User',
            'email': 'user@example.com',
            'password': generate_password_hash('secret123'),
            'role': 'user',
            'is_locked': 0,
        }

        response = client.post(
            '/login',
            data={'email': 'user@example.com', 'password': 'secret123'},
        )

        assert response.status_code == 302
        assert response.location.endswith('/')
        with client.session_transaction() as session:
            assert session['user_id'] == 2
            assert session['user_role'] == 'user'
            assert session['user_email'] == 'user@example.com'

    @patch('controllers.auth.UserModel.find_by_email')
    def test_login_redirects_admin_to_dashboard(self, find_by_email, client):
        find_by_email.return_value = {
            'id': 1,
            'fullname': 'Administrator',
            'email': 'admin@example.com',
            'password': generate_password_hash('secret123'),
            'role': 'admin',
            'is_locked': 0,
        }

        response = client.post(
            '/login',
            data={'email': 'admin@example.com', 'password': 'secret123'},
        )

        assert response.status_code == 302
        assert response.location.endswith('/admin/')

    def test_register_page_renders(self, client):
        response = client.get('/register')

        assert response.status_code == 200
        assert 'Đăng ký' in response.get_data(as_text=True)

    @patch('controllers.auth.UserModel.find_by_email', return_value=None)
    @patch('controllers.auth.UserModel.create', return_value=3)
    def test_register_creates_user_with_hashed_password(self, create, find_by_email, client):
        response = client.post(
            '/register',
            data={
                'fullname': 'New User',
                'email': 'new@example.com',
                'phone': '0912345678',
                'password': 'secret123',
                'password_confirm': 'secret123',
            },
        )

        assert response.status_code == 302
        assert response.location.endswith('/login')
        create.assert_called_once()
        args = create.call_args.args
        assert args[:3] == ('New User', 'new@example.com', '0912345678')
        assert args[3] != 'secret123'

    def test_register_rejects_short_password(self, client):
        response = client.post(
            '/register',
            data={
                'fullname': 'New User',
                'email': 'new@example.com',
                'password': '12345',
                'password_confirm': '12345',
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert 'Mật khẩu phải có ít nhất 6 ký tự.' in response.get_data(as_text=True)

    def test_register_rejects_mismatched_passwords(self, client):
        response = client.post(
            '/register',
            data={
                'fullname': 'New User',
                'email': 'new@example.com',
                'password': 'secret123',
                'password_confirm': 'different',
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert 'Mật khẩu xác nhận không khớp.' in response.get_data(as_text=True)

    def test_logout_clears_session(self, user_session):
        response = user_session.get('/logout')

        assert response.status_code == 302
        assert response.location.endswith('/login')
        with user_session.session_transaction() as session:
            assert 'user_id' not in session
            assert 'user_role' not in session
