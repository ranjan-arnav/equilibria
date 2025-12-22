"""
Reasoning Logger - Transparent logging of all agent decisions.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.models import TradeOffDecision, AdaptationRecord


class ReasoningLogger:
    """
    Logs all agent decisions with full reasoning trails.
    Supports JSON export for transparency and debugging.
    """
    
    def __init__(self, log_dir: str = "logs/decisions"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.decisions: list[TradeOffDecision] = []
        self.adaptations: list[AdaptationRecord] = []
    
    def log_decision(self, decision: TradeOffDecision):
        """Log a trade-off decision."""
        self.decisions.append(decision)
        
        # Write individual decision file
        filepath = self.log_dir / f"decision_{decision.decision_id}.json"
        with open(filepath, 'w') as f:
            json.dump(decision.to_dict(), f, indent=2)
    
    def log_adaptation(self, adaptation: AdaptationRecord):
        """Log an adaptation record."""
        self.adaptations.append(adaptation)
    
    def get_decision_by_id(self, decision_id: str) -> Optional[TradeOffDecision]:
        """Retrieve a specific decision."""
        for d in self.decisions:
            if d.decision_id == decision_id:
                return d
        return None
    
    def export_session(self) -> str:
        """Export all decisions from current session to a single file."""
        filepath = self.log_dir / f"session_{self.session_id}.json"
        
        session_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "total_decisions": len(self.decisions),
            "total_adaptations": len(self.adaptations),
            "decisions": [d.to_dict() for d in self.decisions],
            "adaptations": [a.to_dict() for a in self.adaptations]
        }
        
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return str(filepath)
    
    def get_reasoning_summary(self, last_n: int = 5) -> str:
        """Get a human-readable summary of recent decisions."""
        recent = self.decisions[-last_n:] if len(self.decisions) >= last_n else self.decisions
        
        if not recent:
            return "No decisions logged yet."
        
        lines = [f"=== Last {len(recent)} Decisions ===\n"]
        
        for d in recent:
            lines.append(d.get_summary())
            lines.append("-" * 40)
        
        return "\n".join(lines)
    
    def get_statistics(self) -> dict:
        """Get statistics about logged decisions."""
        if not self.decisions:
            return {"status": "no_decisions"}
        
        from collections import Counter
        from src.models import DecisionAction, HealthDomain
        
        action_counts = Counter()
        domain_actions = {domain: Counter() for domain in HealthDomain}
        constraint_counts = Counter()
        
        for d in self.decisions:
            for constraint in d.constraints_active:
                constraint_counts[constraint] += 1
            
            for dec in d.decisions:
                action_counts[dec.action.value] += 1
                domain_actions[dec.domain][dec.action.value] += 1
        
        return {
            "total_decisions": len(self.decisions),
            "total_adaptations": len(self.adaptations),
            "action_distribution": dict(action_counts),
            "domain_breakdown": {
                domain.value: dict(counts) 
                for domain, counts in domain_actions.items()
            },
            "common_constraints": dict(constraint_counts.most_common(5))
        }
