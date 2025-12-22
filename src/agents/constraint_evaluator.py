"""
Constraint Evaluator Agent - Identifies active constraints limiting adherence.
"""
from dataclasses import dataclass
from typing import Optional

from src.models import HealthState, UserProfile, ActiveConstraints, StressLevel


@dataclass
class ConstraintThresholds:
    """Configurable thresholds for constraint detection."""
    min_sleep_hours: float = 6.0
    critical_sleep_hours: float = 5.0
    low_energy_threshold: int = 4
    critical_energy_threshold: int = 2
    min_time_hours: float = 0.5
    limited_time_hours: float = 1.5
    max_consecutive_high_effort: int = 3
    sleep_debt_warning_hours: float = 3.0
    sleep_debt_critical_hours: float = 6.0


class ConstraintEvaluator:
    """
    Agent that evaluates current health state against thresholds
    and identifies active constraints that limit full adherence.
    
    Constraints are categorized by severity and source, enabling
    the Trade-Off Engine to make informed prioritization decisions.
    """
    
    CONSTRAINT_DESCRIPTIONS = {
        "low_sleep": "Sleep below minimum threshold - recovery impaired",
        "critical_sleep": "Severely sleep deprived - high priority for rest",
        "low_energy": "Energy levels depleted - reduced capacity for effort",
        "critical_energy": "Energy critically low - only essential activities",
        "high_stress": "Elevated stress - cognitive load impaired",
        "time_limited": "Limited time available - must prioritize",
        "time_critical": "Minimal time available - only most critical tasks",
        "overtraining_risk": "Too many consecutive high-effort days",
        "sleep_debt_accumulated": "Accumulated sleep debt needs addressing",
        "burnout_warning": "Multiple indicators suggest burnout risk"
    }
    
    def __init__(
        self,
        user_profile: UserProfile,
        thresholds: Optional[ConstraintThresholds] = None
    ):
        self.user_profile = user_profile
        self.thresholds = thresholds or ConstraintThresholds(
            min_sleep_hours=user_profile.min_sleep_hours
        )
    
    def evaluate(self, state: HealthState) -> ActiveConstraints:
        """
        Evaluate health state and return all active constraints.
        
        Args:
            state: Current HealthState snapshot
            
        Returns:
            ActiveConstraints object with all detected constraints
        """
        constraints = ActiveConstraints()
        
        # Sleep constraints
        self._evaluate_sleep(state, constraints)
        
        # Energy constraints
        self._evaluate_energy(state, constraints)
        
        # Stress constraints
        self._evaluate_stress(state, constraints)
        
        # Time constraints
        self._evaluate_time(state, constraints)
        
        # Effort/overtraining constraints
        self._evaluate_effort(state, constraints)
        
        # Compound constraints (multiple factors)
        self._evaluate_compound(state, constraints)
        
        return constraints
    
    def _evaluate_sleep(self, state: HealthState, constraints: ActiveConstraints):
        """Evaluate sleep-related constraints."""
        if state.sleep_hours < self.thresholds.critical_sleep_hours:
            constraints.add(
                name="critical_sleep",
                severity=0.9,
                description=self.CONSTRAINT_DESCRIPTIONS["critical_sleep"],
                source="wearable"
            )
        elif state.sleep_hours < self.thresholds.min_sleep_hours:
            severity = 1 - (state.sleep_hours / self.thresholds.min_sleep_hours)
            constraints.add(
                name="low_sleep",
                severity=min(0.7, severity),
                description=self.CONSTRAINT_DESCRIPTIONS["low_sleep"],
                source="wearable"
            )
        
        # Sleep debt accumulation
        if state.sleep_debt_hours >= self.thresholds.sleep_debt_critical_hours:
            constraints.add(
                name="sleep_debt_accumulated",
                severity=0.8,
                description=f"Accumulated sleep debt of {state.sleep_debt_hours:.1f} hours",
                source="derived"
            )
        elif state.sleep_debt_hours >= self.thresholds.sleep_debt_warning_hours:
            constraints.add(
                name="sleep_debt_accumulated",
                severity=0.5,
                description=f"Building sleep debt of {state.sleep_debt_hours:.1f} hours",
                source="derived"
            )
    
    def _evaluate_energy(self, state: HealthState, constraints: ActiveConstraints):
        """Evaluate energy-related constraints."""
        if state.energy_level <= self.thresholds.critical_energy_threshold:
            constraints.add(
                name="critical_energy",
                severity=0.9,
                description=self.CONSTRAINT_DESCRIPTIONS["critical_energy"],
                source="derived"
            )
        elif state.energy_level <= self.thresholds.low_energy_threshold:
            severity = 1 - (state.energy_level / (self.thresholds.low_energy_threshold + 2))
            constraints.add(
                name="low_energy",
                severity=min(0.7, severity),
                description=self.CONSTRAINT_DESCRIPTIONS["low_energy"],
                source="derived"
            )
    
    def _evaluate_stress(self, state: HealthState, constraints: ActiveConstraints):
        """Evaluate stress-related constraints."""
        if state.stress_level == StressLevel.HIGH:
            constraints.add(
                name="high_stress",
                severity=0.7,
                description=self.CONSTRAINT_DESCRIPTIONS["high_stress"],
                source="wearable"
            )
    
    def _evaluate_time(self, state: HealthState, constraints: ActiveConstraints):
        """Evaluate time availability constraints."""
        if state.time_available_hours < self.thresholds.min_time_hours:
            constraints.add(
                name="time_critical",
                severity=0.9,
                description=self.CONSTRAINT_DESCRIPTIONS["time_critical"],
                source="user_input"
            )
        elif state.time_available_hours < self.thresholds.limited_time_hours:
            severity = 1 - (state.time_available_hours / self.thresholds.limited_time_hours)
            constraints.add(
                name="time_limited",
                severity=min(0.7, severity),
                description=self.CONSTRAINT_DESCRIPTIONS["time_limited"],
                source="user_input"
            )
    
    def _evaluate_effort(self, state: HealthState, constraints: ActiveConstraints):
        """Evaluate overtraining/effort constraints."""
        if state.consecutive_high_effort_days >= self.thresholds.max_consecutive_high_effort:
            constraints.add(
                name="overtraining_risk",
                severity=0.6,
                description=f"{state.consecutive_high_effort_days} consecutive high-effort days",
                source="derived"
            )
    
    def _evaluate_compound(self, state: HealthState, constraints: ActiveConstraints):
        """
        Evaluate compound constraints - combinations that together
        indicate higher risk than individual factors.
        """
        # Burnout warning: multiple moderate constraints
        risk_factors = 0
        
        if constraints.has("low_sleep") or constraints.has("critical_sleep"):
            risk_factors += 1
        if constraints.has("low_energy") or constraints.has("critical_energy"):
            risk_factors += 1
        if constraints.has("high_stress"):
            risk_factors += 1
        if constraints.has("overtraining_risk"):
            risk_factors += 1
        
        if risk_factors >= 3:
            constraints.add(
                name="burnout_warning",
                severity=0.85,
                description="Multiple risk factors indicate burnout risk",
                source="derived"
            )
    
    def get_constraint_summary(self, constraints: ActiveConstraints) -> str:
        """Generate human-readable constraint summary."""
        if not constraints.constraints:
            return "No active constraints - full adherence possible"
        
        lines = ["Active Constraints:"]
        for c in sorted(constraints.constraints, key=lambda x: -x.severity):
            severity_label = "CRITICAL" if c.severity >= 0.8 else "HIGH" if c.severity >= 0.6 else "MODERATE"
            lines.append(f"  [{severity_label}] {c.name}: {c.description}")
        
        return "\n".join(lines)
