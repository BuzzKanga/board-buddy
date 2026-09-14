"""Tests for authentication endpoints."""

from __future__ import annotations


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/auth/register", json={
            "username": "newuser",
            "password": "secret123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_username(self, client):
        client.post("/auth/register", json={
            "username": "dup",
            "password": "pass1",
        })
        resp = client.post("/auth/register", json={
            "username": "dup",
            "password": "pass2",
        })
        assert resp.status_code == 409

    def test_register_returns_usable_token(self, client):
        resp = client.post("/auth/register", json={
            "username": "tokenuser",
            "password": "pass",
        })
        token = resp.json()["access_token"]
        boards_resp = client.get(
            "/boards",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert boards_resp.status_code == 200


class TestLogin:
    def test_login_success(self, client):
        # The demo user is seeded
        resp = client.post("/auth/login", json={
            "username": "demo",
            "password": "password123",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client):
        resp = client.post("/auth/login", json={
            "username": "demo",
            "password": "wrong",
        })
        assert resp.status_code == 401

    def test_login_unknown_user(self, client):
        resp = client.post("/auth/login", json={
            "username": "nobody",
            "password": "anything",
        })
        assert resp.status_code == 401


class TestProtectedEndpoints:
    def test_no_token_returns_401(self, client):
        resp = client.get("/boards")
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, client):
        resp = client.get(
            "/boards",
            headers={"Authorization": "Bearer bad.token.here"},
        )
        assert resp.status_code == 401
