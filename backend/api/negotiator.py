from fastapi import APIRouter, HTTPException, Depends
from backend.models import GoalNegotiationRequest, GoalNegotiationResponse
from src.agents.goal_negotiator import GoalNegotiator

router = APIRouter()

def get_negotiator():
    # Dependency injection for the negotiator agent
    return GoalNegotiator()

from backend.store import BackendStore

@router.post("", response_model=GoalNegotiationResponse)
def negotiate_goal(request: GoalNegotiationRequest, negotiator: GoalNegotiator = Depends(get_negotiator)):
    try:
        current_state_dict = {}
        if request.current_state:
            current_state_dict = request.current_state.model_dump()

        result = negotiator.evaluate_goal(request.goal, current_state_dict)
        
        # If accepted, save to store
        if result.status == "ACCEPTED":
            BackendStore().update_goal(request.goal)
        
        return GoalNegotiationResponse(
            status=result.status,
            reasoning=result.reasoning,
            counter_proposal=result.counter_proposal,
            risk_score=getattr(result, 'risk_score', 0.0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
