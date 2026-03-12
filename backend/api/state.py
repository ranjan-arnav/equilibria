from fastapi import APIRouter, HTTPException, Body
from typing import List
from backend.models import FullState, HealthState, UserProfile
from backend.store import BackendStore

router = APIRouter()

from backend.models import FullState, HealthState, UserProfile, ComputedMetrics, StressLevel

def calculate_metrics(state: HealthState, history_count: int = 0) -> ComputedMetrics:
    # 1. Sleep Score (0-100)
    # Ideal: 8h. <4h is critical.
    sleep_score = min(100, int((state.sleep_hours / 8.0) * 100))
    if state.sleep_hours > 9: sleep_score -= 10 # Oversleep penalty

    # 2. Readiness Score (0-100)
    # Mix of Energy (40%), Sleep (40%), Stress (20%)
    stress_penalty = 0
    stress_contribution = 0
    if state.stress_level == StressLevel.HIGH: 
        stress_penalty = 30
        stress_contribution = 50 # Weight for risk
    elif state.stress_level == StressLevel.MEDIUM: 
        stress_penalty = 10
        stress_contribution = 20
    
    energy_component = state.energy_level * 10 # 0-100
    readiness = int((energy_component * 0.4) + (sleep_score * 0.4) - stress_penalty)
    readiness = max(0, min(100, readiness + 20)) # Base bump

    # 3. Burnout Risk (0-100)
    # High Stress + Low Energy/Sleep
    
    # Calculate inputs for factor analysis
    inverse_energy = (10 - state.energy_level) * 3
    inverse_sleep = max(0, (8 - state.sleep_hours) * 5)
    
    risk_base = stress_contribution + inverse_energy + inverse_sleep
    burnout_risk = max(0, min(100, int(risk_base)))
    
    # Analyze Primary Factor
    primary_factor = "Insufficient data (Need 5+ sessions)"
    
    if history_count >= 5:
        # Determine max contributor
        factors = {
            "High Stress Load": stress_contribution,
            "Low Energy Reserves": inverse_energy,
            "Sleep Debt": inverse_sleep
        }
        max_factor = max(factors, key=factors.get)
        if factors[max_factor] < 10:
            primary_factor = "None (Stable)"
        else:
            primary_factor = max_factor

    risk_label = "Low Risk"
    if burnout_risk > 70: risk_label = "High Risk"
    elif burnout_risk > 40: risk_label = "Medium Risk"

    return ComputedMetrics(
        readiness_score=readiness,
        sleep_score=sleep_score,
        burnout_risk_score=burnout_risk,
        burnout_risk_label=risk_label,
        burnout_primary_factor=primary_factor
    )

@router.get("", response_model=FullState)
def get_full_state():
    store = BackendStore()
    current_state = store.get_current_state()
    history = store.get_decision_history()
    
    # Calculate fresh metrics on load
    current_state.computed_metrics = calculate_metrics(current_state, history_count=len(history))
    
    return FullState(
        user_profile=store.get_user_profile(),
        current_state=current_state,
        decision_history=history,
        chat_history=store.get_chat_history(),
        daily_tasks=store.get_daily_tasks()
    )

@router.post("/update_metrics", response_model=HealthState)
def update_metrics(state: HealthState):
    store = BackendStore()
    
    # For simulation, we assume the user is "playing" with "what if"
    # We should show the factor immediately IF they have enough history, implies the model is trained.
    # OR, for simulation, maybe we ALWAYS show it? 
    # User said: "Insufficient data... can you do it like after 4-5 sessions".
    # I'll stick to the store history count.
    
    history_len = len(store.get_decision_history())
    
    # Calculate new metrics
    state.computed_metrics = calculate_metrics(state, history_count=history_len)
    
    store.update_current_state(state)
    return state

@router.post("/update_profile", response_model=UserProfile)
def update_profile(profile: UserProfile):
    store = BackendStore()
    store.update_user_profile(profile)
    return profile

@router.post("/update_tasks", response_model=List[dict])
def update_tasks(tasks: List[dict]):
    store = BackendStore()
    store.update_daily_tasks(tasks)
    return tasks

@router.post("/reset_session")
def reset_session():
    store = BackendStore()
    store.clear_decision_history()
    store.clear_chat()
    return {"status": "success", "message": "Session reset"}
