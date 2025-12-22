"""
Decision Model - Represents trade-off decisions made by the agent.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import json
import uuid


class DecisionAction(str, Enum):
    PRIORITIZE = "PRIORITIZE"   # Full execution, high priority
    MAINTAIN = "MAINTAIN"       # Execute as planned
    DOWNGRADE = "DOWNGRADE"     # Reduced version
    DEFER = "DEFER"             # Move to later time
    SKIP = "SKIP"               # Skip entirely


class HealthDomain(str, Enum):
    FITNESS = "fitness"
    NUTRITION = "nutrition"
    RECOVERY = "recovery"
    MINDFULNESS = "mindfulness"


@dataclass
class PlannedTask:
    """A task that was originally planned."""
    domain: HealthDomain
    name: str
    duration_minutes: int
    intensity: float = 0.5  # 0-1 scale
    description: str = ""
    
    def to_dict(self) -> dict:
        return {
            "domain": self.domain.value,
            "name": self.name,
            "duration_minutes": self.duration_minutes,
            "intensity": self.intensity,
            "description": self.description
        }


@dataclass
class DomainDecision:
    """Decision for a single health domain."""
    domain: HealthDomain
    action: DecisionAction
    original_task: Optional[PlannedTask]
    adjusted_task: Optional[PlannedTask]
    reasoning: str
    priority_score: float  # Final calculated priority
    
    def to_dict(self) -> dict:
        return {
            "domain": self.domain.value,
            "action": self.action.value,
            "original": self.original_task.to_dict() if self.original_task else None,
            "adjusted": self.adjusted_task.to_dict() if self.adjusted_task else None,
            "reasoning": self.reasoning,
            "priority_score": round(self.priority_score, 3)
        }


@dataclass
class FutureImpact:
    """Projected impact on future plans."""
    days_affected: int
    adjustment_type: str  # e.g., "intensity_reduction", "rest_day_added"
    description: str
    
    def to_dict(self) -> dict:
        return {
            "days_affected": self.days_affected,
            "type": self.adjustment_type,
            "description": self.description
        }


@dataclass
class TradeOffDecision:
    """
    Complete trade-off decision with full reasoning trail.
    This is the main output of the Trade-Off Decision Engine.
    """
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Input state summary
    state_snapshot: dict = field(default_factory=dict)
    constraints_active: list[str] = field(default_factory=list)
    
    # Priority adjustments made
    priority_adjustments: dict = field(default_factory=dict)
    
    # Individual domain decisions
    decisions: list[DomainDecision] = field(default_factory=list)
    
    # Future adjustments
    future_impacts: list[FutureImpact] = field(default_factory=list)
    
    # Meta
    confidence_score: float = 0.8  # Agent's confidence in this decision
    reasoning_summary: str = ""
    
    def add_decision(self, decision: DomainDecision):
        self.decisions.append(decision)
    
    def add_future_impact(self, impact: FutureImpact):
        self.future_impacts.append(impact)
    
    def get_decision(self, domain: HealthDomain) -> Optional[DomainDecision]:
        for d in self.decisions:
            if d.domain == domain:
                return d
        return None
    
    def to_dict(self) -> dict:
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "state_snapshot": self.state_snapshot,
            "constraints_active": self.constraints_active,
            "priority_adjustments": self.priority_adjustments,
            "decisions": [d.to_dict() for d in self.decisions],
            "future_impacts": [f.to_dict() for f in self.future_impacts],
            "confidence_score": self.confidence_score,
            "reasoning_summary": self.reasoning_summary
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
    
    def get_summary(self) -> str:
        """Generate a human-readable summary of the decision."""
        lines = [f"Decision {self.decision_id} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"]
        lines.append(f"Active Constraints: {', '.join(self.constraints_active) or 'None'}")
        lines.append("\nDecisions:")
        
        for d in self.decisions:
            emoji = {
                DecisionAction.PRIORITIZE: "✓",
                DecisionAction.MAINTAIN: "•",
                DecisionAction.DOWNGRADE: "↓",
                DecisionAction.DEFER: "→",
                DecisionAction.SKIP: "✗"
            }.get(d.action, "?")
            
            if d.original_task:
                original = d.original_task.name
                if d.adjusted_task and d.action == DecisionAction.DOWNGRADE:
                    lines.append(f"  {emoji} {d.domain.value.upper()}: {original} → {d.adjusted_task.name}")
                elif d.action == DecisionAction.SKIP:
                    lines.append(f"  {emoji} {d.domain.value.upper()}: Skip {original}")
                else:
                    lines.append(f"  {emoji} {d.domain.value.upper()}: {original}")
                lines.append(f"      Reason: {d.reasoning}")
        
        if self.future_impacts:
            lines.append("\nFuture Adjustments:")
            for f in self.future_impacts:
                lines.append(f"  • {f.description}")
        
        return "\n".join(lines)


@dataclass
class AdaptationRecord:
    """Record of a pattern-based adaptation."""
    timestamp: datetime
    pattern_detected: str  # e.g., "consistent_skip_fitness", "burnout_risk"
    adaptation_made: str
    affected_domains: list[HealthDomain]
    reasoning: str
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "pattern": self.pattern_detected,
            "adaptation": self.adaptation_made,
            "domains": [d.value for d in self.affected_domains],
            "reasoning": self.reasoning
        }
