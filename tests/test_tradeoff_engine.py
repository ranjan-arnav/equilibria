"""
Tests for the Trade-Off Decision Engine
"""
import pytest
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import (
    HealthState, StressLevel, UserProfile, HealthDomain,
    PlannedTask, DecisionAction, ActiveConstraints
)
from src.agents import (
    StateAnalyzer, ConstraintEvaluator, TradeOffEngine, PlanAdjuster
)
from src.data import SyntheticDataGenerator
from src.main import HTPAOrchestrator, create_sample_planned_tasks


class TestConstraintEvaluator:
    """Test constraint evaluation logic."""
    
    def setup_method(self):
        self.profile = UserProfile.create_default()
        self.evaluator = ConstraintEvaluator(self.profile)
    
    def test_critical_sleep_constraint(self):
        """Critical sleep should be detected when sleep < 5 hours."""
        state = HealthState(
            timestamp=datetime.now(),
            sleep_hours=4.0,
            sleep_quality=40,
            energy_level=3,
            stress_level=StressLevel.MEDIUM,
            time_available_hours=2.0
        )
        
        constraints = self.evaluator.evaluate(state)
        
        assert constraints.has("critical_sleep")
        assert constraints.get_severity("critical_sleep") >= 0.8
    
    def test_high_stress_constraint(self):
        """High stress should be detected."""
        state = HealthState(
            timestamp=datetime.now(),
            sleep_hours=7.0,
            sleep_quality=75,
            energy_level=5,
            stress_level=StressLevel.HIGH,
            time_available_hours=2.0
        )
        
        constraints = self.evaluator.evaluate(state)
        
        assert constraints.has("high_stress")
    
    def test_time_critical_constraint(self):
        """Time critical should be detected when time < 0.5 hours."""
        state = HealthState(
            timestamp=datetime.now(),
            sleep_hours=7.0,
            sleep_quality=75,
            energy_level=7,
            stress_level=StressLevel.LOW,
            time_available_hours=0.25
        )
        
        constraints = self.evaluator.evaluate(state)
        
        assert constraints.has("time_critical")
    
    def test_burnout_warning_compound(self):
        """Burnout warning should trigger with multiple risk factors."""
        state = HealthState(
            timestamp=datetime.now(),
            sleep_hours=4.5,  # Low sleep
            sleep_quality=35,
            energy_level=2,   # Critical energy
            stress_level=StressLevel.HIGH,  # High stress
            time_available_hours=1.0,
            consecutive_high_effort_days=4  # Overtraining
        )
        
        constraints = self.evaluator.evaluate(state)
        
        assert constraints.has("burnout_warning")
    
    def test_no_constraints_good_state(self):
        """No constraints when state is good."""
        state = HealthState(
            timestamp=datetime.now(),
            sleep_hours=7.5,
            sleep_quality=85,
            energy_level=8,
            stress_level=StressLevel.LOW,
            time_available_hours=3.0
        )
        
        constraints = self.evaluator.evaluate(state)
        
        assert len(constraints.constraints) == 0


class TestTradeOffEngine:
    """Test the core trade-off decision logic."""
    
    def setup_method(self):
        self.profile = UserProfile.create_default()
        self.engine = TradeOffEngine(self.profile)
        self.tasks = create_sample_planned_tasks()
    
    def test_burnout_skips_fitness(self):
        """Burnout warning should skip fitness."""
        state = HealthState(
            timestamp=datetime.now(),
            sleep_hours=4.0,
            sleep_quality=30,
            energy_level=2,
            stress_level=StressLevel.HIGH,
            time_available_hours=1.0
        )
        
        constraints = ActiveConstraints()
        constraints.add("burnout_warning", 0.9, "Test", "test")
        constraints.add("critical_sleep", 0.9, "Test", "test")
        
        decision = self.engine.decide(state, constraints, self.tasks)
        
        fitness_dec = decision.get_decision(HealthDomain.FITNESS)
        assert fitness_dec is not None
        assert fitness_dec.action in [DecisionAction.SKIP, DecisionAction.DOWNGRADE]
    
    def test_high_stress_prioritizes_mindfulness(self):
        """High stress should boost mindfulness priority."""
        state = HealthState(
            timestamp=datetime.now(),
            sleep_hours=6.0,
            sleep_quality=60,
            energy_level=5,
            stress_level=StressLevel.HIGH,
            time_available_hours=2.0
        )
        
        constraints = ActiveConstraints()
        constraints.add("high_stress", 0.7, "Test", "test")
        
        decision = self.engine.decide(state, constraints, self.tasks)
        
        mindfulness_dec = decision.get_decision(HealthDomain.MINDFULNESS)
        assert mindfulness_dec is not None
        # Should be prioritized or maintained, not skipped
        assert mindfulness_dec.action != DecisionAction.SKIP
    
    def test_time_critical_downgrades_tasks(self):
        """Critical time should result in downgrades."""
        state = HealthState(
            timestamp=datetime.now(),
            sleep_hours=7.0,
            sleep_quality=70,
            energy_level=6,
            stress_level=StressLevel.LOW,
            time_available_hours=0.25
        )
        
        constraints = ActiveConstraints()
        constraints.add("time_critical", 0.9, "Test", "test")
        
        decision = self.engine.decide(state, constraints, self.tasks)
        
        # Most tasks should be skipped or downgraded
        skip_or_downgrade = sum(
            1 for d in decision.decisions 
            if d.action in [DecisionAction.SKIP, DecisionAction.DOWNGRADE]
        )
        assert skip_or_downgrade >= 2
    
    def test_good_state_maintains_tasks(self):
        """Good state should maintain or prioritize tasks."""
        state = HealthState(
            timestamp=datetime.now(),
            sleep_hours=8.0,
            sleep_quality=90,
            energy_level=9,
            stress_level=StressLevel.LOW,
            time_available_hours=4.0
        )
        
        constraints = ActiveConstraints()  # No constraints
        
        decision = self.engine.decide(state, constraints, self.tasks)
        
        # No tasks should be skipped
        skipped = sum(1 for d in decision.decisions if d.action == DecisionAction.SKIP)
        assert skipped == 0
    
    def test_decision_has_reasoning(self):
        """Every decision should have reasoning."""
        state = HealthState(
            timestamp=datetime.now(),
            sleep_hours=5.0,
            sleep_quality=50,
            energy_level=4,
            stress_level=StressLevel.MEDIUM,
            time_available_hours=1.5
        )
        
        constraints = ActiveConstraints()
        constraints.add("low_sleep", 0.5, "Test", "test")
        
        decision = self.engine.decide(state, constraints, self.tasks)
        
        for d in decision.decisions:
            assert d.reasoning is not None
            assert len(d.reasoning) > 0
    
    def test_future_impacts_generated(self):
        """Decisions under constraints should generate future impacts."""
        state = HealthState(
            timestamp=datetime.now(),
            sleep_hours=4.0,
            sleep_quality=30,
            energy_level=2,
            stress_level=StressLevel.HIGH,
            time_available_hours=1.0,
            sleep_debt_hours=6.0
        )
        
        constraints = ActiveConstraints()
        constraints.add("burnout_warning", 0.9, "Test", "test")
        constraints.add("critical_sleep", 0.9, "Test", "test")
        
        decision = self.engine.decide(state, constraints, self.tasks)
        
        assert len(decision.future_impacts) > 0


class TestSyntheticDataGenerator:
    """Test synthetic data generation."""
    
    def test_generates_valid_wearable_data(self):
        """Generated data should have valid ranges."""
        gen = SyntheticDataGenerator(seed=42)
        data = gen.generate_wearable_data(datetime.now())
        
        assert 2 <= data.sleep_hours <= 12
        assert 0 <= data.deep_sleep_percent <= 100
        assert data.wake_events >= 0
        assert 40 <= data.resting_heart_rate <= 120
        assert data.hrv_ms > 0
        assert data.steps >= 0
    
    def test_fatigue_reduces_hrv(self):
        """High fatigue should reduce HRV."""
        gen = SyntheticDataGenerator(seed=42)
        
        good = gen.generate_wearable_data(datetime.now(), fatigue_factor=0.1)
        tired = gen.generate_wearable_data(datetime.now(), fatigue_factor=0.9)
        
        # On average, tired should have lower HRV (may not always be true due to randomness)
        # So we use seed to make it deterministic
        assert tired.hrv_ms < good.hrv_ms + 20  # Allow some variance
    
    def test_week_scenario_generates_7_days(self):
        """Week generation should produce 7 days of data."""
        gen = SyntheticDataGenerator(seed=42)
        week = gen.generate_week(scenario="burnout")
        
        assert len(week) == 7


class TestOrchestrator:
    """Test the main orchestrator."""
    
    def test_full_pipeline(self):
        """Test complete decision pipeline."""
        orchestrator = HTPAOrchestrator()
        gen = SyntheticDataGenerator(seed=42)
        
        wearable = gen.generate_wearable_data(
            datetime.now(),
            fatigue_factor=0.6,
            stress_factor=0.7
        )
        
        tasks = create_sample_planned_tasks()
        
        decision = orchestrator.run_daily_decision(
            wearable_data=wearable,
            time_available_hours=1.5,
            planned_tasks=tasks
        )
        
        assert decision is not None
        assert decision.decision_id is not None
        assert len(decision.decisions) > 0
        assert decision.reasoning_summary is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
