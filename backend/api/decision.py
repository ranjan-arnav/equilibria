from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from backend.models import HealthState, DecisionAction, HealthDomain
from datetime import datetime
from src.agents.health_council import HealthCouncil
from src.agents.constraint_evaluator import ConstraintEvaluator
from src.models import UserProfile

router = APIRouter()

class DecisionRequest(BaseModel):
    activity: str
    domain: str  # "fitness", "nutrition", etc.
    duration: int
    state: HealthState

class DecisionResponse(BaseModel):
    action: str  # "APPROVED", "MODIFIED", "REJECTED"
    adjustment: Optional[str] = None
    reasoning: str
    constraints: List[str]
    temporal_analysis: Optional[str] = None
    context_assessment: Optional[str] = None

@router.post("", response_model=DecisionResponse)
async def make_decision(request: DecisionRequest):
    try:
        from backend.store import BackendStore
        store = BackendStore()
        
        # 1. Setup Models
        profile = UserProfile(user_id="demo_user", name="User", age=30) 
        
        # 2. Evaluate Constraints (Keep for metadata)
        evaluator = ConstraintEvaluator(profile)
        
        from src.models import HealthState as InternalHealthState, StressLevel as InternalStressLevel
        
        internal_state = InternalHealthState(
            sleep_hours=request.state.sleep_hours,
            energy_level=request.state.energy_level,
            stress_level=InternalStressLevel(request.state.stress_level.lower()),
            time_available_hours=request.state.available_time,
            sleep_debt_hours=0,
            consecutive_high_effort_days=0,
            timestamp=datetime.now(),
            sleep_quality=75.0
        )
        
        constraints = evaluator.evaluate(internal_state)
        
        # 3. Health Council Deliberation
        council = HealthCouncil()
        
        # Need history for Future Self agent
        history = store.get_decision_history()
        
        # State dict for council
        state_dict = {
            "sleep_hours": request.state.sleep_hours,
            "energy_level": request.state.energy_level,
            "stress_level": request.state.stress_level,
            "available_time": request.state.available_time
        }
        
        decision = council.deliberate(
            state_snapshot=state_dict,
            planned_activity=request.activity,
            user_goal=store.get_user_profile().goal,
            decision_history=history
        )
        
        # 4. Save to Store
        
        # Map agent votes
        decisions_list = []
        for vote in decision.agent_votes:
            # Map enum to string if needed
            role_str = vote.agent_role.value if hasattr(vote.agent_role, 'value') else str(vote.agent_role)
            
            # Agent name formatting for UI
            display_name = role_str.replace("_", " ").title()
            if role_str == "sleep": display_name = "Sleep Specialist"
            if role_str == "performance": display_name = "Performance Coach"
            if role_str == "wellness": display_name = "Wellness Guardian"
            if role_str == "future": display_name = "Future Self"

            decisions_list.append({
                "agent_name": display_name,
                "domain": role_str, # Use role as domain key for UI icons if needed
                "vote": vote.action,
                "reasoning": vote.reasoning,
                "confidence": vote.confidence
            })

        record = {
            "timestamp": datetime.now().isoformat(),
            "activity": request.activity,
            "action": decision.final_action,
            "consensus": decision.final_action,
            "decisions": decisions_list,
            "reasoning_summary": decision.reasoning_summary,
            "temporal_analysis": "Consensus Level: " + str(int(decision.consensus_level * 100)) + "%",
            "context_assessment": f"Agreed by {len([v for v in decision.agent_votes if v.action == decision.final_action])}/{len(decision.agent_votes)} agents"
        }
        
        store.add_decision(record)
        
        return DecisionResponse(
            action=decision.final_action,
            adjustment=None, # Council doesn't explicitly return adjustment text structure yet, relying on reasoning
            reasoning=decision.reasoning_summary,
            constraints=[c.name for c in constraints.constraints],
            temporal_analysis=record["temporal_analysis"],
            context_assessment=record["context_assessment"]
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
