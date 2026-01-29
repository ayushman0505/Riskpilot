import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_backend():
    print(f"Testing Backend at {BASE_URL}...")
    
    # 1. Health Check
    try:
        print("\n1. Testing Health Check (GET /)...")
        r = requests.get(f"{BASE_URL}/")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        if r.status_code != 200:
            print("❌ Health Check Failed!")
            return
        print("✅ Health Check Passed!")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    # 2. Create Project
    print("\n2. Testing Create Project (POST /projects)...")
    payload = {
        "name": "Debug Project",
        "description": "Created by debug script",
        "budget": 1000
    }
    try:
        r = requests.post(f"{BASE_URL}/projects", json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 200:
            print("✅ Project Creation Passed!")
            project_id = r.json().get("id")
            print(f"Created Project ID: {project_id}")
        else:
            print("❌ Project Creation Failed!")
            if r.status_code == 404:
                 print("👉 Error 404 suggests the backend is running but the route isn't found.")
                 print("   Check if backend/main.py has @app.post('/projects')")
            if r.status_code == 500:
                 print("👉 Error 500 suggests a server/database error. Check the backend terminal logs!")
    except Exception as e:
        print(f"❌ Request Failed: {e}")
        return

    # 3. Testing Chat Init (POST /chat/init/{id})
    if 'project_id' in locals():
        print(f"\n3. Testing AI Init for Project {project_id}...")
        files = {
            'employee_file': ('emp.csv', 'name,role\nAlice,Dev', 'text/csv'),
            'project_file': ('proj.csv', 'name,deadline\nTest,2024-01-01', 'text/csv'),
            'financial_file': ('fin.csv', 'date,amount\n2024-01-01,100', 'text/csv')
        }
        try:
             r = requests.post(f"{BASE_URL}/chat/init/{project_id}", files=files)
             print(f"Status: {r.status_code}")
             if r.status_code == 200:
                 print("✅ AI Initialization Passed!")
                 print(f"Analysis Preview: {r.json().get('analysis')[:100]}...")
             else:
                 print(f"❌ AI Init Failed: {r.text}")
        except Exception as e:
             print(f"❌ Chat Init Request Failed: {e}")

if __name__ == "__main__":
    test_backend()
