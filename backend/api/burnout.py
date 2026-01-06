from fastapi import APIRouter, HTTPException, Depends
from backend.models import HealthState, BurnoutPredictionResponse
from src.agents.burnout_predictor import BurnoutPredictor

router = APIRouter()

def get_predictor():
    return BurnoutPredictor()

@router.post("/predict", response_model=BurnoutPredictionResponse)
def predict_burnout(state: HealthState, predictor: BurnoutPredictor = Depends(get_predictor)):
    try:
        # Simulate a history of 7 days with this state to predict "what if"
        from src.models import TradeOffDecision
        from datetime import datetime, timedelta
        
        state_dict = state.model_dump()
        
        # Ensure enums are converted to values if needed, or keep as is if the agent handles them
        # The agent expects state_snapshot dicts.
        
        mock_history = []
        for i in range(7):
            mock_date = datetime.now() - timedelta(days=i)
            # We create a dummy TradeOffDecision
            # Note: We need to ensure we populate minimal required fields for the agent
            mock_decision = TradeOffDecision(
                decision_id=f"mock_{i}",
                timestamp=mock_date,
                decisions=[], # Empty list of domain decisions
                state_snapshot=state_dict
            )
            mock_history.append(mock_decision)
            
        forecast = predictor.analyze(mock_history)
        
        # Map fields
        # severity -> risk_level
        # primary_factors -> reasoning
        
        reasoning_text = ", ".join(forecast.primary_factors)
        if not reasoning_text:
            reasoning_text = "Stable behavior patterns detected."
            
        return BurnoutPredictionResponse(
            risk_level=forecast.severity.capitalize(), 
            reasoning=reasoning_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
