from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import random

from backend.store import BackendStore
from backend.models import HealthState, StressLevel, ComputedMetrics
from backend.api.state import calculate_metrics

router = APIRouter()

class SimulationRequest(BaseModel):
    scenario_id: str
    daily_time: float

class DailyProjection(BaseModel):
    day: str
    stress_load: int
    energy_level: int
    readiness_score: int
    metrics: ComputedMetrics

class SimulationResponse(BaseModel):
    projections: List[DailyProjection]
    final_state: HealthState
    insights: List[str]

@router.post("/run", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest):
    store = BackendStore()
    # 1. Enforce Prerequisite: Check if >= 3 decisions made
    history = store.get_decision_history()
    if len(history) < 3:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient data. Please run 'Make Decision' {3 - len(history)} more times to calibrate the agent."
        )

    # 2. Clone Current State
    current_state = store.get_current_state()
    sim_state = current_state.copy()  # Shallow copy is fine for Pydantic model
    # Override time with user input
    sim_state.available_time = request.daily_time
    
    # Apply Scenario Modifiers (Initial Impact)
    if request.scenario_id == 'burnout_recovery':
        sim_state.stress_level = StressLevel.HIGH
        sim_state.energy_level = max(1, sim_state.energy_level - 2)
    elif request.scenario_id == 'preventive':
        sim_state.stress_level = StressLevel.MEDIUM
    elif request.scenario_id == 'peak':
        sim_state.stress_level = StressLevel.LOW
        sim_state.energy_level = min(10, sim_state.energy_level + 2)
    
    projections = []
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # 3. Simulation Loop (7 Days)
    # We simulate "perfect" agent adherence for the simulation to show potential upside
    for day in days:
        # A. Simulate Day Passing (Agent Intervention Effect)
        # Logic: If stress is high, agent reduces it. If energy low, agent boosts it (via sleep/rest).
        
        # Recovery Logic
        if sim_state.stress_level == StressLevel.HIGH:
            # Agent enforces recovery
            sim_state.sleep_hours = min(9.0, sim_state.sleep_hours + 1.0)
            sim_state.stress_level = StressLevel.MEDIUM # Improved
        elif sim_state.stress_level == StressLevel.MEDIUM:
            if sim_state.energy_level > 6:
                # Good outcome
                 sim_state.stress_level = StressLevel.LOW
            else:
                 sim_state.sleep_hours = min(8.5, sim_state.sleep_hours + 0.5)

        # Energy Dynamics
        if sim_state.sleep_hours >= 8.0:
            sim_state.energy_level = min(10, sim_state.energy_level + 1)
        elif sim_state.sleep_hours < 6.0:
             sim_state.energy_level = max(1, sim_state.energy_level - 1)
             
        # Normalize
        sim_state.energy_level = max(1, min(10, int(sim_state.energy_level)))
        sim_state.sleep_hours = float(max(4.0, min(10.0, sim_state.sleep_hours)))
        
        # B. Calculate Metrics for this simulated day
        # We need a dummy history count for the calculation to be valid? 
        # Actually calculate_metrics uses history count for burnout primary factor.
        # We can simulate history growing
        metrics = calculate_metrics(sim_state, history_count=len(history) + len(projections))
        
        # Map Stress Level to "Stress Load" (0-100) for chart
        stress_load = 80 if sim_state.stress_level == StressLevel.HIGH else \
                      50 if sim_state.stress_level == StressLevel.MEDIUM else 20
        
        # Add some daily variance "Noise" to make it look real
        stress_load += random.randint(-5, 5)
        
        projections.append(DailyProjection(
            day=day,
            stress_load=int(stress_load),
            energy_level=int(sim_state.energy_level * 10), # Scale to 0-100
            readiness_score=metrics.readiness_score,
            metrics=metrics
        ))

    # 4. Generate Insights
    avg_readiness = sum(p.readiness_score for p in projections) // 7
    lowest_day = min(projections, key=lambda x: x.readiness_score).day
    
    insights = [
        f"Average readiness for the week: {avg_readiness}%",
        f"Lowest point expected on: {lowest_day}",
        "Recovery protocols effectively manage stress spikes." if avg_readiness > 50 else "High stress load detected. Aggressive recovery recommended."
    ]

    return SimulationResponse(
        projections=projections,
        final_state=sim_state,
        insights=insights
    )
