from fastapi import APIRouter, HTTPException, Depends
from backend.models import CouncilDeliberationRequest, CouncilDeliberationResponse, CouncilAgentVote
from src.agents.health_council import HealthCouncil, ConsensusDecision

from backend.store import BackendStore
from datetime import datetime

router = APIRouter()

def get_council():
    return HealthCouncil()

@router.post("/deliberate", response_model=CouncilDeliberationResponse)
def deliberate(request: CouncilDeliberationRequest, council: HealthCouncil = Depends(get_council)):
    try:
        store = BackendStore()
        
        # Convert Pydantic models to dicts for the agent
        state_dict = request.state.model_dump()
        
        # Use history from STORE, ignore request.decision_history if needed
        # Or better: merge them? For now, let's prefer the store as the source of truth
        history = store.get_decision_history()
        
        decision = council.deliberate(
            state_snapshot=state_dict,
            planned_activity=request.activity,
            user_goal=request.user_goal,
            decision_history=history
        )
        
        # Save this new decision to store
        # We need to serialize the decision result
        record = {
            "timestamp": datetime.now().isoformat(),
            "activity": request.activity,
            "action": decision.final_action,
            "decisions": [
                {"role": v.agent_role.value if hasattr(v.agent_role, 'value') else str(v.agent_role), 
                 "action": v.action,
                 "reasoning": v.reasoning} 
                for v in decision.agent_votes
            ]
        }
        store.add_decision(record)
        
        # Map internal Decision object to API Response
        role_map = {
            "sleep": "Sleep Specialist",
            "performance": "Performance Coach",
            "wellness": "Wellness Guardian",
            "future": "Future Self"
        }

        agents_votes = []
        for vote in decision.agent_votes:
            role_value = vote.agent_role.value if hasattr(vote.agent_role, 'value') else str(vote.agent_role)
            display_name = role_map.get(role_value, role_value.capitalize())
            
            agents_votes.append(CouncilAgentVote(
                agent_name=display_name,
                vote=vote.action,
                confidence=vote.confidence,
                reasoning=vote.reasoning
            ))

        return CouncilDeliberationResponse(
            consensus=decision.final_action,
            confidence=decision.consensus_level,
            agents=agents_votes,
            reasoning_summary=decision.reasoning_summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
