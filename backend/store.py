import json
import os
from typing import List, Optional, Dict
from datetime import datetime
from backend.models import HealthState, UserProfile, DecisionAction, HealthDomain

DATA_FILE = "data/store.json"

class BackendStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BackendStore, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        self.data = {
            "user_profile": {
                "name": "Demo User",
                "age": 25,
                "goal": "Improve overall health"
            },
            "current_state": {
                "sleep_hours": 7.0,
                "energy_level": 6,
                "stress_level": "Medium",
                "available_time": 2.0
            },
            "decision_history": [],
            "chat_history": [],
            "daily_tasks": []
        }
        
        # Ensure data dir exists
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    loaded = json.load(f)
                    # Deep merge or selective update to ensure structure
                    if "user_profile" in loaded: self.data["user_profile"].update(loaded["user_profile"])
                    if "current_state" in loaded: self.data["current_state"].update(loaded["current_state"])
                    if "decision_history" in loaded: self.data["decision_history"] = loaded["decision_history"]
                    if "chat_history" in loaded: self.data["chat_history"] = loaded["chat_history"]
                    if "daily_tasks" in loaded: self.data["daily_tasks"] = loaded["daily_tasks"]
            except Exception as e:
                print(f"Error loading store: {e}, starting fresh.")

    def _save_data(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving store: {e}")

    # --- Accessors ---

    def get_user_profile(self) -> UserProfile:
        return UserProfile(**self.data["user_profile"])

    def update_user_profile(self, profile: UserProfile):
        self.data["user_profile"] = profile.model_dump()
        self._save_data()

    def update_goal(self, goal: str):
        self.data["user_profile"]["goal"] = goal
        self._save_data()

    def get_current_state(self) -> HealthState:
        return HealthState(**self.data["current_state"])

    def update_current_state(self, state: HealthState):
        self.data["current_state"] = state.model_dump()
        self._save_data()

    def get_decision_history(self) -> List[dict]:
        return self.data["decision_history"]

    def add_decision(self, decision_record: dict):
        # Add timestamp if not present
        if "timestamp" not in decision_record:
            decision_record["timestamp"] = datetime.now().isoformat()
        self.data["decision_history"].append(decision_record)
        # Keep last 50 decisions
        if len(self.data["decision_history"]) > 50:
            self.data["decision_history"].pop(0)
        self._save_data()

    def get_chat_history(self) -> List[dict]:
        return self.data["chat_history"]

    def add_chat_message(self, role: str, content: str):
        self.data["chat_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._save_data()
    
    def clear_chat(self):
        self.data["chat_history"] = []
        self._save_data()

    def get_daily_tasks(self) -> List[dict]:
        return self.data.get("daily_tasks", [])

    def update_daily_tasks(self, tasks: List[dict]):
        self.data["daily_tasks"] = tasks
        self._save_data()

    def clear_decision_history(self):
        self.data["decision_history"] = []
        self._save_data()

