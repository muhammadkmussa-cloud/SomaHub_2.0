import time
import httpx

API_ROOT = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"

email = f"smoke+{int(time.time())}@example.com"
password = "Password123!"
username = "smokescript"

print("Using email:", email)

with httpx.Client(base_url=API_ROOT) as client:
    # 1) Signup reader
    signup_payload = {
        "username": username,
        "email": email,
        "password": password,
        "confirm_password": password,
    }
    r = client.post(f"{API_PREFIX}/auth/signup/reader", json=signup_payload)
    print("signup ->", r.status_code, r.text)
    if r.status_code not in (200, 201):
        raise SystemExit("Signup failed")

    user_id = r.json().get("data", {}).get("user_id")
    if not user_id:
        raise SystemExit("No user_id in signup response")

    # 2) Read verification token via debug endpoint (development only)
    r = client.get(f"/internal/debug/verify-token/{user_id}")
    print("debug get ->", r.status_code, r.text)
    token = r.json().get("token")
    if not token:
        raise SystemExit("Verification token not found via debug endpoint")

    # 3) Verify email
    r = client.post(f"{API_PREFIX}/auth/verify-email", json={"token": token})
    print("verify ->", r.status_code, r.text)
    if r.status_code != 200:
        raise SystemExit("Verify failed")

    # 4) Login
    r = client.post(
        f"{API_PREFIX}/auth/login", json={"email": email, "password": password}
    )
    print("login ->", r.status_code, r.text)
    if r.status_code != 200:
        raise SystemExit("Login failed")
    access_token = r.json().get("access_token") or r.json().get("access_token")
    print("access_token present:", bool(access_token))

    # 5) Test refresh-cookie using cookie set by login
    r = client.post(f"{API_PREFIX}/auth/refresh-cookie")
    print("refresh-cookie ->", r.status_code, r.text)

print("Smoke test completed successfully")
