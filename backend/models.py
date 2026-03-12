from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List, Dict
from datetime import datetime

# --- Enums from src/models ---

class DecisionAction(str, Enum):
    PRIORITIZE = "PRIORITIZE"
    MAINTAIN = "MAINTAIN"
    DOWNGRADE = "DOWNGRADE"
    DEFER = "DEFER"
    SKIP = "SKIP"

class HealthDomain(str, Enum):
    FITNESS = "fitness"
    NUTRITION = "nutrition"
    RECOVERY = "recovery"
    MINDFULNESS = "mindfulness"

class StressLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

# --- Models ---

class PlannedTask(BaseModel):
    domain: HealthDomain
    name: str
    duration_minutes: int
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    description: str = ""

class UserProfile(BaseModel):
    name: str = "Demo User"
    age: int = 25
    goal: str = "Improve overall health"

class ComputedMetrics(BaseModel):
    readiness_score: int
    sleep_score: int
    burnout_risk_score: int
    burnout_risk_label: str
    burnout_primary_factor: str

class HealthState(BaseModel):
    sleep_hours: float = 7.0
    energy_level: int = 6
    stress_level: StressLevel = StressLevel.MEDIUM
    available_time: float = 2.0
    computed_metrics: Optional[ComputedMetrics] = None
    
class GoalNegotiationRequest(BaseModel):
    goal: str
    current_state: Optional[HealthState] = None

class GoalNegotiationResponse(BaseModel):
    status: str  # ACCEPTED, NEGOTIATE, REJECTED
    reasoning: str
    counter_proposal: Optional[str] = None
    risk_score: float = 0.0

class CouncilDeliberationRequest(BaseModel):
    activity: str
    state: HealthState
    user_goal: str
    decision_history: List[dict] = []

class CouncilAgentVote(BaseModel):
    agent_name: str
    vote: str # PROCEED, MODIFY, SKIP
    confidence: float
    reasoning: str

class CouncilDeliberationResponse(BaseModel):
    consensus: str # PROCEED, MODIFY, SKIP
    confidence: float
    agents: List[CouncilAgentVote]
    reasoning_summary: str

class BurnoutPredictionResponse(BaseModel):
    risk_level: str
    reasoning: str

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class FullState(BaseModel):
    user_profile: UserProfile
    current_state: HealthState
    decision_history: List[dict]
    chat_history: List[ChatMessage]
    daily_tasks: List[dict] = []
