import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def run_chat_loop():
    print("--- Starting Chat Loop Debugger ---")
    
    # 1. Create Project
    print("\n[1] Creating Project...")
    p = requests.post(f"{BASE_URL}/projects", json={"name": "ChatDebug", "description": "Test", "budget": 500}).json()
    pid = p['id']
    print(f"Project ID: {pid}")

    # 2. Init Chat
    print("\n[2] Initializing Chat...")
    files = {
        'employee_file': ('emp.csv', 'name,role\nAlice,CEO', 'text/csv'),
        'project_file': ('proj.csv', 'name,due\nA,2025', 'text/csv'),
        'financial_file': ('fin.csv', 'date,amt\n2025,100', 'text/csv')
    }
    r = requests.post(f"{BASE_URL}/chat/init/{pid}", files=files)
    if r.status_code != 200:
        print(f"Init Failed: {r.text}")
        return
    print("Init Success.")

    # 3. Loop Messages
    messages = ["Hello", "Who is Alice?", "What is the budget?", "Summarize risks", "Tell me a joke"]
    
    for i, msg in enumerate(messages):
        print(f"\n[3.{i+1}] Sending User Message: '{msg}'")
        try:
            start = time.time()
            res = requests.post(f"{BASE_URL}/chat/continue/{pid}", json={"message": msg})
            params = {"project_id": pid}
            
            print(f"Status: {res.status_code}")
            print(f"Time: {time.time() - start:.2f}s")
            
            if res.status_code == 200:
                print(f"AI Response: {res.json()['response'][:50]}...")
            else:
                print(f"❌ ERROR: {res.text}")
                break
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            break
        
        time.sleep(1) # Be nice to rate limits

if __name__ == "__main__":
    run_chat_loop()
