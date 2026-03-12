import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    try:
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code == 200:
            print("✅ Health Check Passed")
        else:
            print(f"❌ Health Check Failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Health Check Error: {e}")

def test_negotiate(goal="Run a marathon in 1 week"):
    try:
        payload = {"goal": goal}
        resp = requests.post(f"{BASE_URL}/api/negotiate", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Negotiate Check Passed: {data['status']}")
            # print(f"   Reasoning: {data['reasoning']}")
        else:
            print(f"❌ Negotiate Check Failed: {resp.text}")
    except Exception as e:
        print(f"❌ Negotiate Error: {e}")

def test_council(activity="HIIT Workout", state=None):
    if state is None:
        state = {
            "sleep_hours": 6.5,
            "energy_level": 5,
            "stress_level": "Medium",
            "available_time": 1.0
        }
    
    payload = {
        "activity": activity,
        "state": state,
        "user_goal": "Improve Cardiovascular Health",
        "decision_history": []
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/api/council/deliberate", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Council Check Passed: {data['consensus']}")
        else:
            print(f"❌ Council Check Failed: {resp.text}")
            with open("council_error.html", "w") as f:
                f.write(resp.text)
    except Exception as e:
        print(f"❌ Council Error: {e}")

def test_burnout(state=None):
    if state is None:
        state = {
            "sleep_hours": 5.0,
            "energy_level": 3,
            "stress_level": "High",
            "available_time": 0.5
        }
    try:
        resp = requests.post(f"{BASE_URL}/api/burnout/predict", json=state)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Burnout Predictor Check Passed: {data['risk_level']}")
        else:
            print(f"❌ Burnout Check Failed: {resp.text}")
    except Exception as e:
        print(f"❌ Burnout Error: {e}")

def test_chat(message="I am feeling very tired today", state=None):
    payload = {"message": message, "context": state}
    try:
        resp = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Chat Agent Check Passed: {data['response'][:30]}...")
        else:
            print(f"❌ Chat Check Failed: {resp.text}")
    except Exception as e:
        print(f"❌ Chat Error: {e}")

def test_decision(activity="HIIT Workout", state=None):
    if state is None:
        state = {"sleep_hours": 4.5, "stress_level": "High", "energy_level": 3, "available_time": 1.0}
    
    payload = {
        "activity": activity, 
        "domain": "fitness", 
        "duration": 45, 
        "state": state
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/decision", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Decision Engine Check Passed: {data.get('action', 'UNKNOWN')}")
        else:
            print(f"❌ Decision Check Failed: {resp.text}")
    except Exception as e:
        print(f"❌ Decision Error: {e}")

def test_state_persistence():
    print("\n--- Testing State Persistence ---")
    headers = {'Content-Type': 'application/json'}
    
    # 1. Update State
    new_state = {
        "sleep_hours": 5.5,
        "energy_level": 4,
        "stress_level": "High",
        "available_time": 1.0
    }
    resp = requests.post(f"{BASE_URL}/api/state/update_metrics", json=new_state, headers=headers)
    if resp.status_code != 200:
        print("❌ Failed to update state:", resp.text)
        return
        
    # 2. Fetch State to verify
    resp = requests.get(f"{BASE_URL}/api/state")
    if resp.status_code != 200:
        print("❌ Failed to get state:", resp.text)
        return
    
    fetched = resp.json()["current_state"]
    if fetched["sleep_hours"] == 5.5 and fetched["stress_level"] == "High":
        print("✅ State Persistence Verified (Sleep=5.5, Stress=High)")
    else:
        print("❌ State Persistence Failed:", fetched)

def verify_chat_history():
    print("\n--- Testing Chat History ---")
    headers = {'Content-Type': 'application/json'}
    
    # 1. Send Message
    msg = {"message": "Remember this message for history test", "context": None}
    requests.post(f"{BASE_URL}/api/chat", json=msg, headers=headers)
    
    # 2. Check State for history
    resp = requests.get(f"{BASE_URL}/api/state")
    history = resp.json().get("chat_history", [])
    
    found = any(m["content"] == "Remember this message for history test" for m in history)
    if found:
         print("✅ Chat History Verified")
    else:
         print("❌ Chat History Failed to Persist")

if __name__ == "__main__":
    print("Running API Verification...")
    
    shared_state = {
        "sleep_hours": 7.5,
        "energy_level": 8,
        "stress_level": "Low",
        "available_time": 2.0
    }
    
    test_health()
    test_negotiate()
    test_council(state=shared_state)
    test_burnout()
    test_chat(state=shared_state)
    test_decision(state=shared_state)
    
    test_state_persistence()
    verify_chat_history()
    
    print("✨ All Backend Checks Completed")
