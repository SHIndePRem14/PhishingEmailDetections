def test_registration_creates_user(client, db):
    response = client.post("/register", data={
        "name": "New User",
        "email": "newuser@example.com",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
    }, follow_redirects=True)
    assert response.status_code == 200

    from app.models.user import User
    user = User.query.filter_by(email="newuser@example.com").first()
    assert user is not None
    assert user.check_password("StrongPass123!")


def test_login_success(client, sample_user):
    response = client.post("/login", data={
        "email": "test@example.com",
        "password": "TestPass123!",
    }, follow_redirects=True)
    assert response.status_code == 200


def test_login_invalid_password(client, sample_user):
    response = client.post("/login", data={
        "email": "test@example.com",
        "password": "WrongPassword",
    }, follow_redirects=True)
    assert b"Invalid email or password" in response.data


def test_logout_requires_login(client):
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in" in response.data or b"Login" in response.data


def test_unauthorized_admin_access(client, sample_user):
    client.post("/login", data={"email": "test@example.com", "password": "TestPass123!"})
    response = client.get("/admin/", follow_redirects=True)
    assert response.status_code == 403
