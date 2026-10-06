import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY='test-secret-key',
        UPLOAD_FOLDER=str(tmp_path),
    )
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user_session(client):
    with client.session_transaction() as session:
        session.update(
            user_id=2,
            user_fullname='Test User',
            user_email='user@example.com',
            user_role='user',
        )
    return client


@pytest.fixture()
def admin_session(client):
    with client.session_transaction() as session:
        session.update(
            user_id=1,
            user_fullname='Test Admin',
            user_email='admin@example.com',
            user_role='admin',
        )
    return client
