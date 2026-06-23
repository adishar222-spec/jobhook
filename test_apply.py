import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test():
    # 1. Login or create user
    print("Logging in...")
    try:
        res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Auto Apply Tester",
            "email": f"tester_{int(time.time())}@example.com",
            "password": "password123",
            "confirm_password": "password123"
        })
        if res.status_code == 409: # Already registered, let's login
            pass
    except Exception as e:
        print("Registration err", e)
        
    res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "name": "Auto Apply Tester",
        "email": "autoapply@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    
    if res.status_code == 409:
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "autoapply@example.com",
            "password": "password123"
        })
        
    token = res.json()["access_token"]
    
    # 2. Trigger auto-apply
    print("Triggering auto-apply...")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(f"{BASE_URL}/api/apply/confirm", json={
        "job_url": "https://www.linkedin.com/jobs/view/12345",
        "platform": "linkedin",
        "application_id": "test_id"
    }, headers=headers)
    
    print(res.status_code, res.text)
    
if __name__ == "__main__":
    test()
