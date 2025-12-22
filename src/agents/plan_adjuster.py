"""
Plan Adjuster Agent - Rebalances future plans based on decisions and patterns.
"""
from datetime import datetime, timedelta
from typing import Optional

from src.models import (
    UserProfile, TradeOffDecision, DecisionAction, HealthDomain,
    PlannedTask, AdaptationRecord
)


class PatternDetector:
    """Detects patterns in decision history for adaptation."""
    
    def __init__(self, history: list[TradeOffDecision]):
        self.history = history
    
    def get_skip_frequency(self, domain: HealthDomain, days: int = 7) -> float:
        """Calculate how often a domain is skipped."""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [d for d in self.history if d.timestamp >= cutoff]
        
        if not recent:
            return 0.0
        
        skips = sum(
            1 for d in recent
            for dec in d.decisions
            if dec.domain == domain and dec.action == DecisionAction.SKIP
        )
        
        return skips / len(recent)
    
    def get_downgrade_frequency(self, domain: HealthDomain, days: int = 7) -> float:
        """Calculate how often a domain is downgraded."""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [d for d in self.history if d.timestamp >= cutoff]
        
        if not recent:
            return 0.0
        
        downgrades = sum(
            1 for d in recent
            for dec in d.decisions
            if dec.domain == domain and dec.action == DecisionAction.DOWNGRADE
        )
        
        return downgrades / len(recent)
    
    def detect_constraint_pattern(self, days: int = 7) -> dict[str, int]:
        """Count frequency of each constraint type."""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [d for d in self.history if d.timestamp >= cutoff]
        
        counts = {}
        for d in recent:
            for c in d.constraints_active:
                counts[c] = counts.get(c, 0) + 1
        
        return counts
    
    def detect_day_of_week_patterns(self) -> dict[int, dict]:
        """Analyze patterns by day of week."""
        patterns = {i: {"decisions": 0, "constraints": 0, "skips": 0} for i in range(7)}
        
        for d in self.history:
            dow = d.timestamp.weekday()
            patterns[dow]["decisions"] += 1
            patterns[dow]["constraints"] += len(d.constraints_active)
            patterns[dow]["skips"] += sum(
                1 for dec in d.decisions if dec.action == DecisionAction.SKIP
            )
        
        # Calculate averages
        for dow, data in patterns.items():
            if data["decisions"] > 0:
                data["avg_constraints"] = data["constraints"] / data["decisions"]
                data["skip_rate"] = data["skips"] / data["decisions"]
        
        return patterns


class PlanAdjuster:
    """
    Agent that adjusts future plans based on today's decisions
    and historical patterns.
    
    Responsibilities:
    - Modify upcoming workload based on current decisions
    - Detect patterns requiring long-term adjustments
    - Prevent burnout through proactive planning
    - Track adaptations for transparency
    """
    
    def __init__(self, user_profile: UserProfile):
        self.user_profile = user_profile
        self.adaptation_history: list[AdaptationRecord] = []
    
    def adjust_future_plan(
        self,
        current_decision: TradeOffDecision,
        upcoming_tasks: list[PlannedTask],
        decision_history: list[TradeOffDecision]
    ) -> tuple[list[PlannedTask], list[AdaptationRecord]]:
        """
        Adjust upcoming tasks based on current decision and patterns.
        
        Args:
            current_decision: Today's trade-off decision
            upcoming_tasks: Planned tasks for coming days
            decision_history: Historical decisions for pattern detection
            
        Returns:
            - Adjusted list of upcoming tasks
            - List of adaptations made with explanations
        """
        adjusted_tasks = list(upcoming_tasks)
        adaptations = []
        
        # Apply immediate adjustments from current decision
        adjusted_tasks, imm_adaptations = self._apply_immediate_adjustments(
            current_decision, adjusted_tasks
        )
        adaptations.extend(imm_adaptations)
        
        # Detect and apply pattern-based adjustments
        if len(decision_history) >= 3:
            pattern_detector = PatternDetector(decision_history)
            adjusted_tasks, pattern_adaptations = self._apply_pattern_adjustments(
                pattern_detector, adjusted_tasks
            )
            adaptations.extend(pattern_adaptations)
        
        # Store adaptations
        self.adaptation_history.extend(adaptations)
        
        return adjusted_tasks, adaptations
    
    def _apply_immediate_adjustments(
        self,
        decision: TradeOffDecision,
        tasks: list[PlannedTask]
    ) -> tuple[list[PlannedTask], list[AdaptationRecord]]:
        """Apply adjustments based on today's specific decision."""
        adjusted = []
        adaptations = []
        
        # Check for intensity reduction from future impacts
        intensity_reduction = 1.0
        for impact in decision.future_impacts:
            if impact.adjustment_type == "intensity_reduction":
                intensity_reduction = 0.6
                break
            elif impact.adjustment_type == "deload_week":
                intensity_reduction = 0.5
                break
        
        for task in tasks:
            new_task = PlannedTask(
                domain=task.domain,
                name=task.name,
                duration_minutes=task.duration_minutes,
                intensity=task.intensity * intensity_reduction,
                description=task.description
            )
            
            # If fitness was skipped, add recovery walk to fitness tasks
            fitness_skipped = any(
                d.domain == HealthDomain.FITNESS and d.action == DecisionAction.SKIP
                for d in decision.decisions
            )
            
            if fitness_skipped and task.domain == HealthDomain.FITNESS:
                # First upcoming fitness becomes lighter
                new_task = PlannedTask(
                    domain=HealthDomain.FITNESS,
                    name="Recovery workout",
                    duration_minutes=min(30, task.duration_minutes),
                    intensity=0.4,
                    description="Lighter workout following rest day"
                )
            
            adjusted.append(new_task)
        
        if intensity_reduction < 1.0:
            adaptations.append(AdaptationRecord(
                timestamp=datetime.now(),
                pattern_detected="high_fatigue_signals",
                adaptation_made=f"Reduced all workout intensities to {int(intensity_reduction*100)}%",
                affected_domains=[HealthDomain.FITNESS],
                reasoning="Based on current fatigue indicators, reducing intensity to support recovery"
            ))
        
        return adjusted, adaptations
    
    def _apply_pattern_adjustments(
        self,
        detector: PatternDetector,
        tasks: list[PlannedTask]
    ) -> tuple[list[PlannedTask], list[AdaptationRecord]]:
        """Apply adjustments based on detected patterns."""
        adjusted = list(tasks)
        adaptations = []
        
        # Check for consistently skipped domains
        for domain in HealthDomain:
            skip_rate = detector.get_skip_frequency(domain)
            
            if skip_rate > 0.5:  # Skipped more than half the time
                # This domain may be unrealistic - reduce expectations
                for i, task in enumerate(adjusted):
                    if task.domain == domain:
                        adjusted[i] = PlannedTask(
                            domain=domain,
                            name=f"Flexible {task.name}",
                            duration_minutes=int(task.duration_minutes * 0.7),
                            intensity=task.intensity * 0.8,
                            description=f"Adjusted based on adherence patterns: {task.description}"
                        )
                
                adaptations.append(AdaptationRecord(
                    timestamp=datetime.now(),
                    pattern_detected=f"consistent_skip_{domain.value}",
                    adaptation_made=f"Reduced {domain.value} expectations by 30%",
                    affected_domains=[domain],
                    reasoning=f"{domain.value} is skipped {skip_rate*100:.0f}% of the time - adjusting to more realistic targets"
                ))
        
        # Check for chronic constraint patterns
        constraint_counts = detector.detect_constraint_pattern()
        
        if constraint_counts.get("high_stress", 0) >= 4:  # High stress 4+ days in a week
            adaptations.append(AdaptationRecord(
                timestamp=datetime.now(),
                pattern_detected="chronic_high_stress",
                adaptation_made="Increased mindfulness allocation, reduced fitness intensity",
                affected_domains=[HealthDomain.MINDFULNESS, HealthDomain.FITNESS],
                reasoning="Persistent high stress pattern - rebalancing priorities for stress management"
            ))
        
        if constraint_counts.get("low_sleep", 0) >= 5:
            adaptations.append(AdaptationRecord(
                timestamp=datetime.now(),
                pattern_detected="chronic_sleep_deficit",
                adaptation_made="Recommend sleep hygiene review and reduced evening activities",
                affected_domains=[HealthDomain.RECOVERY],
                reasoning="Consistent sleep issues detected - systemic adjustment recommended"
            ))
        
        return adjusted, adaptations
    
    def generate_weekly_adjustment_report(
        self,
        decision_history: list[TradeOffDecision]
    ) -> dict:
        """Generate a summary of adaptations and patterns for the week."""
        if len(decision_history) < 3:
            return {"status": "insufficient_data"}
        
        detector = PatternDetector(decision_history)
        
        report = {
            "period": "last_7_days",
            "total_decisions": len(decision_history),
            "domains": {},
            "constraint_frequency": detector.detect_constraint_pattern(),
            "day_patterns": detector.detect_day_of_week_patterns(),
            "adaptations_made": len(self.adaptation_history),
            "recommendations": []
        }
        
        # Domain-level analysis
        for domain in HealthDomain:
            report["domains"][domain.value] = {
                "skip_rate": round(detector.get_skip_frequency(domain) * 100, 1),
                "downgrade_rate": round(detector.get_downgrade_frequency(domain) * 100, 1)
            }
        
        # Generate recommendations
        for domain, stats in report["domains"].items():
            if stats["skip_rate"] > 40:
                report["recommendations"].append(
                    f"Consider reducing {domain} targets - current plan may be too ambitious"
                )
            elif stats["downgrade_rate"] > 60:
                report["recommendations"].append(
                    f"{domain} frequently downgraded - consider adjusting default intensity"
                )
        
        high_stress_days = report["constraint_frequency"].get("high_stress", 0)
        if high_stress_days >= 4:
            report["recommendations"].append(
                "High stress is frequent - consider adding more recovery buffers"
            )
        
        return report
