"""
Multi-Agent Health Council - Collaborative Decision Making System
Each specialized agent provides recommendations that are combined via weighted consensus.
Now with LLM-enhanced reasoning for smarter decisions.
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from groq import Groq
except ImportError:
    Groq = None


class AgentRole(Enum):
    """Specialized agent roles in the health council."""
    SLEEP_SPECIALIST = "sleep"
    PERFORMANCE_COACH = "performance"
    WELLNESS_GUARDIAN = "wellness"
    FUTURE_SELF = "future"


@dataclass
class AgentRecommendation:
    """A single agent's recommendation."""
    agent_role: AgentRole
    action: str  # "PROCEED", "MODIFY", "SKIP"
    reasoning: str
    confidence: float  # 0.0 to 1.0
    priority_adjustment: dict[str, float]  # Domain -> priority multiplier


@dataclass
class ConsensusDecision:
    """Final decision reached by the council."""
    final_action: str
    consensus_level: float  # 0.0 to 1.0 (agreement among agents)
    agent_votes: list[AgentRecommendation]
    reasoning_summary: str
    dissenting_opinions: list[str]


class SleepSpecialistAgent:
    """Prioritizes recovery, rest, and circadian health."""
    
    def __init__(self):
        self.role = AgentRole.SLEEP_SPECIALIST
        self.priority_weights = {
            "Sleep": 1.5,
            "Recovery": 1.3,
            "Exercise": 0.7,  # Lower priority when sleep-deprived
            "Work": 0.6
        }
    
    def recommend(self, state_snapshot: dict, planned_activity: str) -> AgentRecommendation:
        """Provide recommendation based on sleep/recovery needs."""
        sleep_hours = state_snapshot.get('sleep_hours', 7)
        energy = state_snapshot.get('energy_level', 5)
        
        # Critical sleep debt
        if sleep_hours < 6:
            if "HIIT" in planned_activity or "Intense" in planned_activity:
                return AgentRecommendation(
                    agent_role=self.role,
                    action="SKIP",
                    reasoning=f"Sleep debt detected ({sleep_hours}h). High-intensity exercise increases cortisol and impairs recovery.",
                    confidence=0.95,
                    priority_adjustment={"Sleep": 2.0, "Exercise": 0.3}
                )
        
        # Moderate sleep debt
        if sleep_hours < 7:
            return AgentRecommendation(
                agent_role=self.role,
                action="MODIFY",
                reasoning=f"Suboptimal sleep ({sleep_hours}h). Recommend lower intensity to preserve recovery capacity.",
                confidence=0.75,
                priority_adjustment={"Sleep": 1.5, "Exercise": 0.7}
            )
        
        # Good sleep
        return AgentRecommendation(
            agent_role=self.role,
            action="PROCEED",
            reasoning=f"Adequate sleep ({sleep_hours}h). Recovery capacity is good.",
            confidence=0.8,
            priority_adjustment={}
        )


class PerformanceCoachAgent:
    """Maximizes productivity and goal achievement."""
    
    def __init__(self):
        self.role = AgentRole.PERFORMANCE_COACH
        self.priority_weights = {
            "Work": 1.4,
            "Exercise": 1.3,
            "Learning": 1.2,
            "Sleep": 0.9
        }
    
    def recommend(self, state_snapshot: dict, planned_activity: str, user_goal: str) -> AgentRecommendation:
        """Provide recommendation based on performance optimization."""
        energy = state_snapshot.get('energy_level', 5)
        
        # High energy - maximize output
        if energy >= 7:
            if "Exercise" in planned_activity or "Work" in planned_activity:
                return AgentRecommendation(
                    agent_role=self.role,
                    action="PROCEED",
                    reasoning=f"High energy ({energy}/10). Optimal window for high-value activities aligned with goal: {user_goal}",
                    confidence=0.9,
                    priority_adjustment={"Work": 1.5, "Exercise": 1.4}
                )
        
        # Low energy - strategic rest
        if energy <= 3:
            return AgentRecommendation(
                agent_role=self.role,
                action="MODIFY",
                reasoning=f"Low energy ({energy}/10). Recommend strategic rest to prevent diminishing returns.",
                confidence=0.7,
                priority_adjustment={"Sleep": 1.3, "Work": 0.6}
            )
        
        # Moderate energy
        return AgentRecommendation(
            agent_role=self.role,
            action="PROCEED",
            reasoning=f"Moderate energy ({energy}/10). Maintain planned activities.",
            confidence=0.6,
            priority_adjustment={}
        )


class WellnessGuardianAgent:
    """Balances mental health, stress, and overall wellbeing."""
    
    def __init__(self):
        self.role = AgentRole.WELLNESS_GUARDIAN
        self.priority_weights = {
            "Mindfulness": 1.5,
            "Social": 1.3,
            "Recovery": 1.2,
            "Work": 0.7
        }
    
    def recommend(self, state_snapshot: dict, planned_activity: str) -> AgentRecommendation:
        """Provide recommendation based on stress and wellness."""
        stress = state_snapshot.get('stress_level', 'MODERATE')
        
        # High stress - intervention needed
        if isinstance(stress, str) and stress.upper() == 'HIGH':
            if "Work" in planned_activity or "Deadline" in planned_activity:
                return AgentRecommendation(
                    agent_role=self.role,
                    action="SKIP",
                    reasoning="High stress detected. Additional cognitive load risks burnout. Recommend stress-reduction activities.",
                    confidence=0.85,
                    priority_adjustment={"Mindfulness": 2.0, "Work": 0.4}
                )
        
        # Moderate stress
        if isinstance(stress, str) and stress.upper() == 'MODERATE':
            return AgentRecommendation(
                agent_role=self.role,
                action="MODIFY",
                reasoning="Moderate stress. Balance productivity with recovery activities.",
                confidence=0.7,
                priority_adjustment={"Mindfulness": 1.3}
            )
        
        # Low stress
        return AgentRecommendation(
            agent_role=self.role,
            action="PROCEED",
            reasoning="Stress levels manageable. Maintain current balance.",
            confidence=0.75,
            priority_adjustment={}
        )


class FutureSelfAgent:
    """Advocates for long-term consequences and habit formation."""
    
    def __init__(self):
        self.role = AgentRole.FUTURE_SELF
    
    def recommend(self, state_snapshot: dict, decision_history: list, planned_activity: str) -> AgentRecommendation:
        """Provide recommendation based on long-term patterns."""
        # Analyze recent skip patterns
        recent_skips = [d for d in decision_history[-7:] if any(
            dec.action.value == "SKIP" for dec in d.decisions
        )]
        
        skip_rate = len(recent_skips) / max(len(decision_history[-7:]), 1)
        
        # High skip rate - pattern forming
        if skip_rate > 0.5:
            return AgentRecommendation(
                agent_role=self.role,
                action="PROCEED",
                reasoning=f"Skip rate is {skip_rate:.0%} this week. Skipping again risks habit collapse. Your future self needs consistency.",
                confidence=0.9,
                priority_adjustment={}
            )
        
        # Moderate skip rate
        if skip_rate > 0.3:
            return AgentRecommendation(
                agent_role=self.role,
                action="MODIFY",
                reasoning=f"Skip rate is {skip_rate:.0%}. Consider a lighter version to maintain habit momentum.",
                confidence=0.7,
                priority_adjustment={}
            )
        
        # Good consistency
        return AgentRecommendation(
            agent_role=self.role,
            action="PROCEED",
            reasoning=f"Good consistency ({skip_rate:.0%} skip rate). Your future self will thank you.",
            confidence=0.8,
            priority_adjustment={}
        )


class HealthCouncil:
    """Orchestrates multi-agent deliberation and consensus."""
    
    def __init__(self):
        self.sleep_specialist = SleepSpecialistAgent()
        self.performance_coach = PerformanceCoachAgent()
        self.wellness_guardian = WellnessGuardianAgent()
        self.future_self = FutureSelfAgent()
        
        # Initialize Groq client for LLM deliberation
        api_key = os.getenv("GROQ_API_KEY")
        self.llm_client = Groq(api_key=api_key) if api_key and Groq else None
    
    def deliberate(
        self, 
        state_snapshot: dict, 
        planned_activity: str,
        user_goal: str,
        decision_history: list
    ) -> ConsensusDecision:
        """Gather recommendations - uses LLM if available, otherwise heuristic agents."""
        
        # Try LLM-based deliberation first
        if self.llm_client:
            try:
                return self._llm_deliberate(state_snapshot, planned_activity, user_goal)
            except Exception as e:
                print(f"LLM deliberation failed: {e}")
                # Fall through to heuristic
        
        # Heuristic-based deliberation (original logic)
        return self._heuristic_deliberate(state_snapshot, planned_activity, user_goal, decision_history)
    
    def _llm_deliberate(self, state_snapshot: dict, planned_activity: str, user_goal: str) -> ConsensusDecision:
        """Use LLM for intelligent circuit breaker decision."""
        prompt = f"""You are a Health Safety Council evaluating if an activity is safe.

USER STATE:
- Sleep: {state_snapshot.get('sleep_hours', 7)}h
- Energy: {state_snapshot.get('energy_level', 5)}/10
- Stress: {state_snapshot.get('stress_level', 'Medium')}

PLANNED ACTIVITY: {planned_activity}
USER GOAL: {user_goal}

Evaluate if this activity is safe given the user's current state.

Output STRICT JSON:
{{
  "action": "PROCEED" | "MODIFY" | "SKIP",
  "consensus_level": 0.0-1.0,
  "primary_reasoning": "One sentence explanation",
  "agent_opinions": [
    {{"role": "sleep", "action": "PROCEED|MODIFY|SKIP", "reasoning": "...", "confidence": 0.0-1.0}},
    {{"role": "performance", "action": "...", "reasoning": "...", "confidence": 0.0-1.0}},
    {{"role": "wellness", "action": "...", "reasoning": "...", "confidence": 0.0-1.0}},
    {{"role": "future", "action": "...", "reasoning": "...", "confidence": 0.0-1.0}}
  ]
}}

Safety Rules:
- SKIP if sleep < 5h AND activity is high intensity
- MODIFY if stress is High AND activity is cognitive
- Consider user goal when evaluating
"""
        response = self.llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        import json
        data = json.loads(response.choices[0].message.content)
        
        # Convert to our data structures
        votes = []
        role_map = {"sleep": AgentRole.SLEEP_SPECIALIST, "performance": AgentRole.PERFORMANCE_COACH,
                    "wellness": AgentRole.WELLNESS_GUARDIAN, "future": AgentRole.FUTURE_SELF}
        
        for opinion in data.get("agent_opinions", []):
            votes.append(AgentRecommendation(
                agent_role=role_map.get(opinion.get("role", "sleep"), AgentRole.SLEEP_SPECIALIST),
                action=opinion.get("action", "PROCEED"),
                reasoning=opinion.get("reasoning", ""),
                confidence=float(opinion.get("confidence", 0.7)),
                priority_adjustment={}
            ))
        
        final_action = data.get("action", "PROCEED")
        dissenting = [f"{v.agent_role.value}: {v.reasoning}" for v in votes if v.action != final_action]
        
        return ConsensusDecision(
            final_action=final_action,
            consensus_level=float(data.get("consensus_level", 0.7)),
            agent_votes=votes,
            reasoning_summary=data.get("primary_reasoning", "LLM-based decision"),
            dissenting_opinions=dissenting
        )
    
    def _heuristic_deliberate(
        self, 
        state_snapshot: dict, 
        planned_activity: str,
        user_goal: str,
        decision_history: list
    ) -> ConsensusDecision:
        """Original heuristic-based consensus (fallback)."""
        
        # Collect votes
        votes = [
            self.sleep_specialist.recommend(state_snapshot, planned_activity),
            self.performance_coach.recommend(state_snapshot, planned_activity, user_goal),
            self.wellness_guardian.recommend(state_snapshot, planned_activity),
            self.future_self.recommend(state_snapshot, decision_history, planned_activity)
        ]
        
        # Calculate consensus
        action_counts = {}
        for vote in votes:
            action_counts[vote.action] = action_counts.get(vote.action, 0) + vote.confidence
        
        # Weighted majority
        final_action = max(action_counts, key=action_counts.get)
        total_confidence = sum(action_counts.values())
        consensus_level = action_counts[final_action] / total_confidence if total_confidence > 0 else 0
        
        # Identify dissenting opinions
        dissenting = [
            f"{vote.agent_role.value}: {vote.reasoning}"
            for vote in votes
            if vote.action != final_action
        ]
        
        # Build reasoning summary
        majority_votes = [v for v in votes if v.action == final_action]
        reasoning_summary = f"Council Decision ({consensus_level:.0%} consensus): {final_action}\n"
        reasoning_summary += "\n".join([f"• {v.agent_role.value}: {v.reasoning}" for v in majority_votes])
        
        return ConsensusDecision(
            final_action=final_action,
            consensus_level=consensus_level,
            agent_votes=votes,
            reasoning_summary=reasoning_summary,
            dissenting_opinions=dissenting
        )
