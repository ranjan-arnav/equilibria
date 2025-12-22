"""
HTPA Main Orchestrator - Coordinates all agents for decision-making.
"""
from datetime import datetime
from typing import Optional

from src.models import (
    UserProfile, HealthState, WearableData, StressLevel,
    TradeOffDecision, PlannedTask, HealthDomain
)
from src.agents import StateAnalyzer, ConstraintEvaluator, TradeOffEngine, PlanAdjuster
from src.data import SyntheticDataGenerator, CSVDataLoader, HistoryTracker
from src.core import ReasoningLogger, get_llm_generator, LLMReasoningGenerator


class HTPAOrchestrator:
    """
    Main orchestrator that coordinates all HTPA agents.
    
    Pipeline:
    1. State Analyzer ingests data → HealthState
    2. Constraint Evaluator identifies limits → ActiveConstraints
    3. Trade-Off Engine makes decisions → TradeOffDecision
    4. Plan Adjuster modifies future → Adjusted Plans
    5. LLM Generator creates natural language explanation
    """
    
    def __init__(
        self, 
        user_profile: Optional[UserProfile] = None,
        llm_generator: Optional[LLMReasoningGenerator] = None
    ):
        self.user_profile = user_profile or UserProfile.create_default()
        
        # Initialize agents
        self.state_analyzer = StateAnalyzer(self.user_profile)
        self.constraint_evaluator = ConstraintEvaluator(self.user_profile)
        self.tradeoff_engine = TradeOffEngine(self.user_profile)
        self.plan_adjuster = PlanAdjuster(self.user_profile)
        
        # LLM for natural language explanations
        self.llm_generator = llm_generator or get_llm_generator()
        
        # Logging
        self.logger = ReasoningLogger()
        
        # State
        self.current_state: Optional[HealthState] = None
        self.last_decision: Optional[TradeOffDecision] = None
        self.last_llm_explanation: Optional[str] = None
    
    def run_daily_decision(
        self,
        wearable_data: WearableData,
        time_available_hours: float,
        planned_tasks: list[PlannedTask],
        user_stress: Optional[StressLevel] = None,
        user_energy: Optional[int] = None
    ) -> TradeOffDecision:
        """
        Run the full decision pipeline for today.
        
        Args:
            wearable_data: Today's wearable data
            time_available_hours: User's available time
            planned_tasks: Originally planned tasks
            user_stress: Optional user-reported stress override
            user_energy: Optional user-reported energy override
            
        Returns:
            Complete TradeOffDecision with reasoning
        """
        # Step 1: Analyze state
        self.current_state = self.state_analyzer.analyze(
            wearable_data=wearable_data,
            time_available_hours=time_available_hours,
            user_reported_stress=user_stress,
            user_reported_energy=user_energy
        )
        
        # Step 2: Evaluate constraints
        constraints = self.constraint_evaluator.evaluate(self.current_state)
        
        # Step 3: Make trade-off decision
        decision = self.tradeoff_engine.decide(
            state=self.current_state,
            constraints=constraints,
            planned_tasks=planned_tasks
        )
        
        # Step 4: Generate LLM explanation (if available)
        self.last_llm_explanation = self.llm_generator.generate_explanation(
            decision_summary=decision.to_dict(),
            state_snapshot=self.current_state.to_dict(),
            constraints=constraints.to_list()
        )
        
        # Step 5: Log decision
        self.logger.log_decision(decision)
        self.last_decision = decision
        
        return decision
    
    def get_llm_explanation(self) -> Optional[str]:
        """Get the last LLM-generated explanation."""
        return self.last_llm_explanation
    
    def run_from_csv(
        self,
        csv_path: str,
        time_available_hours: float,
        planned_tasks: list[PlannedTask],
        target_date: Optional[datetime] = None
    ) -> TradeOffDecision:
        """
        Run decision pipeline using CSV data.
        """
        # Load and analyze from CSV
        self.current_state = self.state_analyzer.analyze_from_csv(
            csv_path=csv_path,
            time_available_hours=time_available_hours,
            target_date=target_date
        )
        
        # Continue with standard pipeline
        constraints = self.constraint_evaluator.evaluate(self.current_state)
        decision = self.tradeoff_engine.decide(
            state=self.current_state,
            constraints=constraints,
            planned_tasks=planned_tasks
        )
        
        self.logger.log_decision(decision)
        self.last_decision = decision
        
        return decision
    
    def get_adaptation_report(self) -> dict:
        """Get weekly adaptation and pattern report."""
        return self.plan_adjuster.generate_weekly_adjustment_report(
            self.tradeoff_engine.decision_history
        )
    
    def get_trend_analysis(self, days: int = 7) -> dict:
        """Get trend analysis from state analyzer."""
        return self.state_analyzer.get_trend_analysis(days)
    
    def export_session(self) -> str:
        """Export all decisions to file."""
        return self.logger.export_session()
    
    def get_reasoning_summary(self) -> str:
        """Get human-readable summary of recent decisions."""
        return self.logger.get_reasoning_summary()


def create_sample_planned_tasks() -> list[PlannedTask]:
    """Create a sample set of planned tasks for demo."""
    return [
        PlannedTask(
            domain=HealthDomain.FITNESS,
            name="HIIT Workout",
            duration_minutes=45,
            intensity=0.8,
            description="High-intensity interval training"
        ),
        PlannedTask(
            domain=HealthDomain.NUTRITION,
            name="Meal Prep",
            duration_minutes=60,
            intensity=0.3,
            description="Prepare healthy meals for the week"
        ),
        PlannedTask(
            domain=HealthDomain.RECOVERY,
            name="Sleep Optimization",
            duration_minutes=30,
            intensity=0.1,
            description="Wind-down routine before bed"
        ),
        PlannedTask(
            domain=HealthDomain.MINDFULNESS,
            name="Meditation Session",
            duration_minutes=20,
            intensity=0.2,
            description="Guided mindfulness meditation"
        )
    ]


def run_demo():
    """Run a quick demo of the system."""
    print("=" * 60)
    print("HTPA - Health Trade-Off & Prioritization Agent Demo")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = HTPAOrchestrator()
    
    # Generate synthetic data for a stressed, sleep-deprived day
    generator = SyntheticDataGenerator(seed=42)
    wearable = generator.generate_wearable_data(
        date=datetime.now(),
        fatigue_factor=0.7,
        stress_factor=0.8
    )
    
    print(f"\n📊 Today's Wearable Data:")
    print(f"   Sleep: {wearable.sleep_hours}h (Quality: {wearable.sleep_quality_score:.0f}/100)")
    print(f"   HRV: {wearable.hrv_ms}ms | Resting HR: {wearable.resting_heart_rate}bpm")
    print(f"   Steps: {wearable.steps} | Active mins: {wearable.active_minutes}")
    
    # Create planned tasks
    tasks = create_sample_planned_tasks()
    
    print(f"\n📋 Originally Planned Tasks:")
    for t in tasks:
        print(f"   • {t.name} ({t.duration_minutes}min, {t.domain.value})")
    
    # Run decision
    decision = orchestrator.run_daily_decision(
        wearable_data=wearable,
        time_available_hours=1.5,  # Limited time
        planned_tasks=tasks
    )
    
    print(f"\n🤖 Agent Decision:")
    print(decision.get_summary())
    
    print(f"\n📌 Reasoning Summary: {decision.reasoning_summary}")
    print(f"   Confidence: {decision.confidence_score:.0%}")
    
    if decision.future_impacts:
        print(f"\n🔮 Future Adjustments:")
        for impact in decision.future_impacts:
            print(f"   • {impact.description}")
    
    # Export
    export_path = orchestrator.export_session()
    print(f"\n💾 Full reasoning log exported to: {export_path}")
    
    return orchestrator


if __name__ == "__main__":
    run_demo()
