"""
Multi-Agent Health Council - Collaborative Decision Making System
Each specialized agent provides recommendations that are combined via weighted consensus.
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum


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
    
    def deliberate(
        self, 
        state_snapshot: dict, 
        planned_activity: str,
        user_goal: str,
        decision_history: list
    ) -> ConsensusDecision:
        """Gather recommendations from all agents and reach consensus."""
        
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
