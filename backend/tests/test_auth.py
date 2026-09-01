def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test_admin@septeria.gov.in",
            "password": "TestPass123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test_admin@septeria.gov.in"
    assert data["user"]["role"] == "admin"

def test_login_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test_admin@septeria.gov.in",
            "password": "WrongPassword123!",
        },
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_protected_me_endpoint_with_valid_token(client):
    # 1. Login to get token
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test_commander@septeria.gov.in",
            "password": "TestPass123!",
        },
    )
    token = login_res.json()["access_token"]

    # 2. Access protected endpoint
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    data = me_res.json()
    assert data["email"] == "test_commander@septeria.gov.in"
    assert data["role"] == "commander"

def test_protected_me_endpoint_without_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_rbac_commander_endpoint_authorization(client):
    # 1. Login as commander (allowed)
    cmd_login = client.post(
        "/api/v1/auth/login",
        json={"email": "test_commander@septeria.gov.in", "password": "TestPass123!"},
    )
    cmd_token = cmd_login.json()["access_token"]

    cmd_check = client.get(
        "/api/v1/auth/verify-commander",
        headers={"Authorization": f"Bearer {cmd_token}"},
    )
    assert cmd_check.status_code == 200

    # 2. Login as personnel (forbidden)
    psn_login = client.post(
        "/api/v1/auth/login",
        json={"email": "test_personnel@septeria.gov.in", "password": "TestPass123!"},
    )
    psn_token = psn_login.json()["access_token"]

    psn_check = client.get(
        "/api/v1/auth/verify-commander",
        headers={"Authorization": f"Bearer {psn_token}"},
    )
    assert psn_check.status_code == 403
