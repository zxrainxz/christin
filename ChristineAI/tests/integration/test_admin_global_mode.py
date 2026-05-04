from __future__ import annotations

import pytest

from app.config import get_settings


@pytest.mark.asyncio
async def test_global_admin_can_list_and_update_all_users(client) -> None:
    settings = get_settings()
    previous_key = settings.admin_api_key
    settings.admin_api_key = "secret-admin-key"

    try:
        reg_a = await client.post("/api/v1/auth/register", json={"email": "ga@test.com", "password": "strongpass1"})
        assert reg_a.status_code == 201
        reg_b = await client.post("/api/v1/auth/register", json={"email": "gb@test.com", "password": "strongpass2"})
        assert reg_b.status_code == 201

        login = await client.post("/api/v1/auth/login", json={"email": "ga@test.com", "password": "strongpass1"})
        assert login.status_code == 200
        token = login.json()["access_token"]

        headers_without_admin = {"Authorization": f"Bearer {token}"}
        headers_admin = {"Authorization": f"Bearer {token}", "X-Admin-Key": "secret-admin-key"}

        users_forbidden = await client.get("/api/v1/admin/users", headers=headers_without_admin)
        assert users_forbidden.status_code == 403

        users_ok = await client.get("/api/v1/admin/users", headers=headers_admin)
        assert users_ok.status_code == 200
        users = users_ok.json()
        assert len(users) == 2

        user_b = next(u for u in users if u["email"] == "gb@test.com")
        patch = await client.patch(
            f"/api/v1/admin/users/{user_b['id']}",
            json={"plan": "pro"},
            headers=headers_admin,
        )
        assert patch.status_code == 200
        assert patch.json()["plan"] == "pro"
    finally:
        settings.admin_api_key = previous_key
