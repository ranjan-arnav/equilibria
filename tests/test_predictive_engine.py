
import pytest
from datetime import datetime
from src.models.health_state import HealthState, StressLevel, EnergyLevel
from src.models.predictive_engine import ReadinessForecaster, WorkloadRecommender, BurnoutClassifier, BurnoutRisk

@pytest.fixture
def mock_health_state():
    return HealthState(
        timestamp=datetime.now(),
        sleep_hours=7.0,
        sleep_quality=80.0,
        energy_level=6,
        stress_level=StressLevel.MEDIUM,
        time_available_hours=2.0,
        sleep_debt_hours=1.0,
        consecutive_high_effort_days=1
    )

def test_readiness_forecaster(mock_health_state):
    # Test base case
    prediction = ReadinessForecaster.predict_tomorrow(mock_health_state)
    assert 0 <= prediction <= 100
    
    # Test good recovery factors
    mock_health_state.stress_level = StressLevel.LOW
    mock_health_state.sleep_debt_hours = 0
    high_prediction = ReadinessForecaster.predict_tomorrow(mock_health_state)
    assert high_prediction > prediction  # Should improve

def test_workload_recommender(mock_health_state):
    # Case: High Stress + High Energy -> Boxing
    mock_health_state.stress_level = StressLevel.HIGH
    mock_health_state.energy_level = 8
    rec = WorkloadRecommender.get_recommendation(mock_health_state)
    assert "Boxing" in rec.activity_type or "HIIT" in rec.activity_type
    
    # Case: Low Energy + High Stress -> Yoga
    mock_health_state.energy_level = 2
    rec = WorkloadRecommender.get_recommendation(mock_health_state)
    assert "Yoga" in rec.activity_type

def test_burnout_classifier(mock_health_state):
    # Case: Low Risk
    risk, reason = BurnoutClassifier.assess_risk(mock_health_state)
    assert risk in [BurnoutRisk.LOW, BurnoutRisk.MODERATE]
    
    # Case: Critical Risk (High debt + stress + load)
    mock_health_state.sleep_debt_hours = 10
    mock_health_state.stress_level = StressLevel.HIGH
    mock_health_state.consecutive_high_effort_days = 4
    
    risk, reason = BurnoutClassifier.assess_risk(mock_health_state)
    assert risk == BurnoutRisk.CRITICAL
    assert "sleep debt" in reason
    assert "consecutive" in reason
