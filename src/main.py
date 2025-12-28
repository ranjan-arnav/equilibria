"""
HTPA Main Orchestrator - Coordinates all agents for decision-making.
"""
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv() # Force load .env

try:
    from groq import Groq
except ImportError:
    Groq = None

from src.models import (
    UserProfile, HealthState, WearableData, StressLevel,
    TradeOffDecision, PlannedTask, HealthDomain
)
from src.agents import StateAnalyzer, ConstraintEvaluator, TradeOffEngine, PlanAdjuster
from src.data import SyntheticDataGenerator, CSVDataLoader, HistoryTracker
from src.core import ReasoningLogger, get_llm_generator, LLMReasoningGenerator


def generate_daily_schedule_llm(user_goal: str = "") -> list[dict]:
    """Generate a full day schedule using LLM based on user goal."""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not user_goal or not api_key or not Groq:
        # Fallback to default schedule
        return [
            {"time": "6:30", "title": "Morning Workout", "type": "high_intensity", "icon": "🏋️"},
            {"time": "8:00", "title": "Standup", "type": "work", "icon": "💼"},
            {"time": "12:00", "title": "Lunch Walk", "type": "recovery", "icon": "🚶"},
            {"time": "3:00", "title": "Deep Work", "type": "cognitive", "icon": "🧠"},
            {"time": "6:00", "title": "Evening Activity", "type": "high_intensity", "icon": "🏃"},
            {"time": "9:00", "title": "Wind-Down", "type": "recovery", "icon": "🌙"},
        ]
    
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": """Generate a daily schedule for someone with this goal.
Output STRICT JSON:
{"schedule": [
  {"time": "HH:MM", "title": "Activity", "type": "high_intensity|work|recovery|cognitive", "icon": "emoji"}
]}
Include 6 items spanning 6AM-10PM. Types: high_intensity (exercise), work (job), recovery (rest/walk), cognitive (focus)."""},
                {"role": "user", "content": f"Goal: {user_goal}"}
            ],
            response_format={"type": "json_object"}
        )
        import json
        data = json.loads(response.choices[0].message.content)
        return data.get("schedule", [])[:6]
    except:
        return [
            {"time": "6:30", "title": "Morning Workout", "type": "high_intensity", "icon": "🏋️"},
            {"time": "8:00", "title": "Standup", "type": "work", "icon": "💼"},
            {"time": "12:00", "title": "Lunch Walk", "type": "recovery", "icon": "🚶"},
            {"time": "3:00", "title": "Deep Work", "type": "cognitive", "icon": "🧠"},
            {"time": "6:00", "title": "Evening Activity", "type": "high_intensity", "icon": "🏃"},
            {"time": "9:00", "title": "Wind-Down", "type": "recovery", "icon": "🌙"},
        ]


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


def create_sample_planned_tasks(user_goal: str = "") -> list[PlannedTask]:
    """Create a sample set of planned tasks, customized by goal (using LLM or Heuristics)."""
    
    # 1. Try LLM Generation (Agentic)
    api_key = os.getenv("GROQ_API_KEY")
    
    # DEBUG: Return debug task if key missing
    if user_goal and not api_key:
         return [PlannedTask(domain=HealthDomain.RECOVERY, name="DEBUG: No API Key", duration_minutes=0, intensity=0, description="Check .env")]

    # DEBUG: Check if Groq lib is missing
    if user_goal and api_key and not Groq:
         return [PlannedTask(domain=HealthDomain.RECOVERY, name="DEBUG: Install 'groq'", duration_minutes=0, intensity=0, description="pip install groq")]

    if user_goal and api_key and Groq:
        try:
            client = Groq(api_key=api_key)
            system_prompt = """You are an expert Fitness Planner. Generate exactly 4 daily tasks based on user Goal.

CRITICAL REQUIREMENTS:
1. FIRST task MUST be domain "Fitness" (exercise/workout/training)
2. Second task MUST be domain "Nutrition" (eating/hydration)
3. Third and fourth tasks can be "Recovery" or "Mindfulness"

Output STRICT JSON:
{"tasks": [
  {"domain": "Fitness", "name": "EXERCISE NAME", "duration_minutes": 45, "intensity": 0.7, "description": "..."},
  {"domain": "Nutrition", "name": "...", "duration_minutes": 30, "intensity": 0.3, "description": "..."},
  {"domain": "Recovery", "name": "...", "duration_minutes": 20, "intensity": 0.2, "description": "..."},
  {"domain": "Mindfulness", "name": "...", "duration_minutes": 15, "intensity": 0.1, "description": "..."}
]}

The FIRST task MUST ALWAYS have domain "Fitness".
"""
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Goal: {user_goal}"}
                ],
                response_format={"type": "json_object"}
            )
            import json
            data = json.loads(response.choices[0].message.content)
            tasks = []
            
            # Handle if wrapped in a key or raw list
            items = data.get("tasks", []) if isinstance(data, dict) else data
            # Fallback if specific key expected (Llama 3 sometimes wraps in "tasks")
            if not items and isinstance(data, dict): 
                # Try to find any list value
                for v in data.values():
                    if isinstance(v, list):
                        items = v
                        break
            
            for item in items:
                # Map domain string to Enum
                d_str = item.get("domain", "Fitness").upper()
                domain_map = {
                    "FITNESS": HealthDomain.FITNESS,
                    "NUTRITION": HealthDomain.NUTRITION,
                    "RECOVERY": HealthDomain.RECOVERY,
                    "MINDFULNESS": HealthDomain.MINDFULNESS
                }
                domain = domain_map.get(d_str, HealthDomain.FITNESS)
                
                tasks.append(PlannedTask(
                    domain=domain,
                    name=item.get("name", "Activity"),
                    duration_minutes=int(item.get("duration_minutes", 30)),
                    intensity=float(item.get("intensity", 0.5)),
                    description=item.get("description", "")
                ))
            
            if tasks:
                return tasks
                
        except Exception as e:
            # DEBUG: Return error as task to see it in UI
            return [PlannedTask(domain=HealthDomain.RECOVERY, name=f"Err: {str(e)[:20]}", duration_minutes=0, intensity=0, description=str(e))]

    # 2. HEURISTIC FALLBACK (Regex)
    # Base Tasks
    tasks = [
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
        )
    ]
    
    # Dynamic Additions based on User Goal
    goal_lower = user_goal.lower()
    
    if "muscle" in goal_lower or "strength" in goal_lower or "bulk" in goal_lower:
        tasks.insert(0, PlannedTask(
            domain=HealthDomain.FITNESS,
            name="Heavy Lifting",
            duration_minutes=60,
            intensity=0.9,
            description="Compound lifts for hypertrophy"
        ))
    elif "run" in goal_lower or "cardio" in goal_lower or "endurance" in goal_lower:
        tasks.insert(0, PlannedTask(
            domain=HealthDomain.FITNESS,
            name="Long Run",
            duration_minutes=90,
            intensity=0.75,
            description="Zone 2 aerobic base building"
        ))
    elif "stress" in goal_lower or "anxiety" in goal_lower or "calm" in goal_lower:
        tasks.append(PlannedTask(
            domain=HealthDomain.MINDFULNESS,
            name="Deep Breathing",
            duration_minutes=15,
            intensity=0.1,
            description="Box breathing for vagus nerve activation"
        ))
        # Swap HIIT for Yoga if high stress focus
        tasks.insert(0, PlannedTask(
            domain=HealthDomain.FITNESS,
            name="Restorative Yoga",
            duration_minutes=45,
            intensity=0.3,
            description="Gentle movement for cortisol reduction"
        ))
        return tasks # Return early to avoid adding HIIT default

    # Default Fitness Task if no specific fitness goal found
    if not any(t.domain == HealthDomain.FITNESS for t in tasks):
        tasks.insert(0, PlannedTask(
            domain=HealthDomain.FITNESS,
            name="HIIT Workout",
            duration_minutes=45,
            intensity=0.8,
            description="High-intensity interval training"
        ))
        
    # Default Mindfulness
    if "stress" not in goal_lower:
         tasks.append(PlannedTask(
            domain=HealthDomain.MINDFULNESS,
            name="Meditation Session",
            duration_minutes=20,
            intensity=0.2,
            description="Guided mindfulness meditation"
        ))

    return tasks


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
