"""
Multi-Day Simulation - Shows autonomous adaptation over a week.
"""
import time
from datetime import datetime, timedelta
from typing import Generator, Optional

from src.models import (
    UserProfile, TradeOffDecision, PlannedTask, HealthDomain
)
from src.data import SyntheticDataGenerator
from src.main import HTPAOrchestrator, create_sample_planned_tasks


class SimulationResult:
    """Result of a single simulated day."""
    
    def __init__(
        self,
        day: int,
        date: datetime,
        decision: TradeOffDecision,
        wearable_summary: dict,
        llm_explanation: Optional[str] = None
    ):
        self.day = day
        self.date = date
        self.decision = decision
        self.wearable_summary = wearable_summary
        self.llm_explanation = llm_explanation
    
    def to_dict(self) -> dict:
        return {
            "day": self.day,
            "date": self.date.strftime("%Y-%m-%d"),
            "wearable": self.wearable_summary,
            "decision": self.decision.to_dict(),
            "explanation": self.llm_explanation
        }


class WeekSimulator:
    """
    Simulates a full week of autonomous agent decisions.
    Shows how the agent adapts over time.
    """
    
    SCENARIOS = {
        "burnout_recovery": {
            "name": "Burnout to Recovery",
            "description": "Start stressed, watch agent enforce recovery",
            "fatigue_curve": [0.9, 0.85, 0.7, 0.5, 0.4, 0.25, 0.15],
            "stress_curve": [0.9, 0.8, 0.65, 0.5, 0.35, 0.25, 0.2]
        },
        "gradual_burnout": {
            "name": "Gradual Burnout",
            "description": "Watch agent detect and prevent burnout",
            "fatigue_curve": [0.2, 0.3, 0.45, 0.6, 0.75, 0.85, 0.9],
            "stress_curve": [0.2, 0.3, 0.4, 0.55, 0.7, 0.8, 0.85]
        },
        "weekend_warrior": {
            "name": "Weekend Warrior",
            "description": "Low effort weekdays, high weekends",
            "fatigue_curve": [0.6, 0.65, 0.7, 0.75, 0.5, 0.2, 0.3],
            "stress_curve": [0.6, 0.65, 0.6, 0.65, 0.4, 0.15, 0.2]
        },
        "high_performer": {
            "name": "High Performer",
            "description": "Consistently good state",
            "fatigue_curve": [0.15, 0.2, 0.15, 0.25, 0.2, 0.1, 0.15],
            "stress_curve": [0.2, 0.25, 0.2, 0.3, 0.2, 0.15, 0.2]
        }
    }
    
    def __init__(
        self,
        scenario: str = "burnout_recovery",
        seed: int = 42
    ):
        self.scenario_config = self.SCENARIOS.get(scenario, self.SCENARIOS["burnout_recovery"])
        self.generator = SyntheticDataGenerator(seed=seed)
        self.orchestrator = HTPAOrchestrator()
        self.results: list[SimulationResult] = []
    
    def run_simulation(
        self,
        days: int = 7,
        time_available_hours: float = 2.0
    ) -> list[SimulationResult]:
        """
        Run a full week simulation and return results.
        """
        self.results = []
        start_date = datetime.now()
        planned_tasks = create_sample_planned_tasks()
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            # Get scenario curves
            fatigue = self.scenario_config["fatigue_curve"][day % 7]
            stress = self.scenario_config["stress_curve"][day % 7]
            
            # Generate wearable data
            wearable = self.generator.generate_wearable_data(
                date=current_date,
                fatigue_factor=fatigue,
                stress_factor=stress,
                is_weekend=(day % 7 >= 5)
            )
            
            # Run decision
            decision = self.orchestrator.run_daily_decision(
                wearable_data=wearable,
                time_available_hours=time_available_hours,
                planned_tasks=planned_tasks
            )
            
            # Get LLM explanation
            llm_explanation = self.orchestrator.get_llm_explanation()
            
            # Create summary from current state
            current_state = self.orchestrator.current_state
            
            daily_metrics = {
                "sleep_hours": wearable.sleep_hours,
                "hrv_ms": wearable.hrv_ms,
                "resting_hr": wearable.resting_heart_rate,
                "steps": wearable.steps,
                "sleep_quality": wearable.sleep_quality_score,
                "readiness_score": current_state.readiness_score if current_state else 0,
                "sleep_debt": current_state.sleep_debt_hours if current_state else 0
            }
            
            result = SimulationResult(
                day=day + 1,
                date=current_date,
                decision=decision,
                wearable_summary=daily_metrics,
                llm_explanation=llm_explanation
            )
            
            self.results.append(result)
        
        return self.results
    
    def run_simulation_streaming(
        self,
        days: int = 7,
        time_available_hours: float = 2.0,
        delay_seconds: float = 0.5
    ) -> Generator[SimulationResult, None, None]:
        """
        Stream simulation results day-by-day for animated display.
        """
        start_date = datetime.now()
        planned_tasks = create_sample_planned_tasks()
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            fatigue = self.scenario_config["fatigue_curve"][day % 7]
            stress = self.scenario_config["stress_curve"][day % 7]
            
            wearable = self.generator.generate_wearable_data(
                date=current_date,
                fatigue_factor=fatigue,
                stress_factor=stress,
                is_weekend=(day % 7 >= 5)
            )
            
            decision = self.orchestrator.run_daily_decision(
                wearable_data=wearable,
                time_available_hours=time_available_hours,
                planned_tasks=planned_tasks
            )
            
            llm_explanation = self.orchestrator.get_llm_explanation()
            
            # Create summary from current state
            current_state = self.orchestrator.current_state
            
            daily_metrics = {
                "sleep_hours": wearable.sleep_hours,
                "hrv_ms": wearable.hrv_ms,
                "resting_hr": wearable.resting_heart_rate,
                "steps": wearable.steps,
                "sleep_quality": wearable.sleep_quality_score,
                "readiness_score": current_state.readiness_score if current_state else 0,
                "sleep_debt": current_state.sleep_debt_hours if current_state else 0
            }
            
            result = SimulationResult(
                day=day + 1,
                date=current_date,
                decision=decision,
                wearable_summary=daily_metrics,
                llm_explanation=llm_explanation
            )
            
            self.results.append(result)
            
            time.sleep(delay_seconds)
            yield result
    
    def get_week_summary(self) -> dict:
        """Get aggregated stats for the week."""
        if not self.results:
            return {"status": "no_simulation_run"}
        
        from collections import Counter
        from src.models import DecisionAction
        
        action_counts = Counter()
        domain_actions = {d.value: Counter() for d in HealthDomain}
        constraints_seen = Counter()
        
        total_sleep = 0
        burnout_days = 0
        
        for r in self.results:
            for d in r.decision.decisions:
                action_counts[d.action.value] += 1
                domain_actions[d.domain.value][d.action.value] += 1
            
            for c in r.decision.constraints_active:
                constraints_seen[c] += 1
            
            total_sleep += r.wearable_summary["sleep_hours"]
            
            if "burnout_warning" in r.decision.constraints_active:
                burnout_days += 1
        
        return {
            "days_simulated": len(self.results),
            "scenario": self.scenario_config["name"],
            "total_decisions": sum(action_counts.values()),
            "action_breakdown": dict(action_counts),
            "domain_breakdown": {k: dict(v) for k, v in domain_actions.items()},
            "constraints_frequency": dict(constraints_seen.most_common(5)),
            "average_sleep": round(total_sleep / len(self.results), 1),
            "burnout_days_detected": burnout_days,
            "adaptation_events": len(self.orchestrator.plan_adjuster.adaptation_history)
        }


def run_demo():
    """Demo the simulation."""
    print("=" * 60)
    print("HTPA 7-Day Simulation: Burnout to Recovery")
    print("=" * 60)
    
    sim = WeekSimulator(scenario="burnout_recovery")
    results = sim.run_simulation()
    
    for r in results:
        print(f"\n📅 Day {r.day} ({r.date.strftime('%A')})")
        print(f"   Sleep: {r.wearable_summary['sleep_hours']}h | HRV: {r.wearable_summary['hrv_ms']}ms")
        print(f"   Constraints: {', '.join(r.decision.constraints_active) or 'None'}")
        
        for d in r.decision.decisions:
            emoji = {"PRIORITIZE": "✓", "MAINTAIN": "•", "DOWNGRADE": "↓", "SKIP": "✗"}.get(d.action.value, "?")
            print(f"   {emoji} {d.domain.value}: {d.action.value}")
    
    print("\n" + "=" * 60)
    print("Week Summary:")
    summary = sim.get_week_summary()
    print(f"   Actions: {summary['action_breakdown']}")
    print(f"   Avg Sleep: {summary['average_sleep']}h")
    print(f"   Burnout Days: {summary['burnout_days_detected']}")
    print(f"   Adaptations: {summary['adaptation_events']}")


if __name__ == "__main__":
    run_demo()
