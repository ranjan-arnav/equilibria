"""
Temporal Reasoning Engine - Analyzes decisions across past, present, and future timelines.
Detects recurring patterns, assesses current context, and projects future outcomes.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from collections import Counter


@dataclass
class RecurringPattern:
    """A detected pattern in user behavior."""
    pattern_type: str  # "weekly", "situational", "trigger-based"
    description: str
    frequency: float  # 0.0 to 1.0
    confidence: float
    examples: list[str]


@dataclass
class PresentContext:
    """Current moment assessment."""
    day_of_week: str
    time_of_day: str
    similar_past_situations: list[dict]
    risk_level: str  # "low", "moderate", "high", "critical"
    risk_factors: list[str]


@dataclass
class FutureTrajectory:
    """Projected outcome based on current path."""
    timeline: str  # "24h", "1 week", "1 month"
    predicted_outcome: str
    probability: float
    impact_level: str  # "minor", "moderate", "major", "severe"
    intervention_window: Optional[str]


@dataclass
class TemporalInsight:
    """Complete temporal analysis."""
    past_patterns: list[RecurringPattern]
    present_context: PresentContext
    future_trajectories: list[FutureTrajectory]
    recommendation: str
    urgency_level: int  # 1-5


class TemporalReasoner:
    """Analyzes decisions across time to provide context-aware insights."""
    
    def __init__(self):
        self.pattern_threshold = 0.6  # 60% frequency to be considered a pattern
    
    def analyze_timeline(
        self, 
        decision_history: list,
        current_state: dict
    ) -> TemporalInsight:
        """Perform complete temporal analysis."""
        
        past_patterns = self.detect_recurring_patterns(decision_history)
        present_context = self.assess_present_moment(decision_history, current_state)
        future_trajectories = self.project_outcomes(past_patterns, present_context, current_state)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            past_patterns, present_context, future_trajectories
        )
        
        # Calculate urgency
        urgency = self._calculate_urgency(present_context, future_trajectories)
        
        return TemporalInsight(
            past_patterns=past_patterns,
            present_context=present_context,
            future_trajectories=future_trajectories,
            recommendation=recommendation,
            urgency_level=urgency
        )
    
    def detect_recurring_patterns(self, history: list) -> list[RecurringPattern]:
        """Detect patterns in historical decisions."""
        if len(history) < 7:
            return []
        
        patterns = []
        
        # Pattern 1: Day-of-week patterns
        dow_skips = self._analyze_day_of_week_patterns(history)
        if dow_skips:
            patterns.extend(dow_skips)
        
        # Pattern 2: Stress-triggered patterns
        stress_patterns = self._analyze_stress_patterns(history)
        if stress_patterns:
            patterns.extend(stress_patterns)
        
        # Pattern 3: Sleep-debt cascades
        sleep_cascades = self._analyze_sleep_cascades(history)
        if sleep_cascades:
            patterns.extend(sleep_cascades)
        
        return patterns
    
    def _analyze_day_of_week_patterns(self, history: list) -> list[RecurringPattern]:
        """Detect day-of-week specific patterns."""
        patterns = []
        
        # Group by day of week
        dow_decisions = {}
        for decision in history:
            dow = decision.timestamp.strftime("%A")
            if dow not in dow_decisions:
                dow_decisions[dow] = []
            dow_decisions[dow].append(decision)
        
        # Check each day for skip patterns
        for dow, decisions in dow_decisions.items():
            if len(decisions) < 2:
                continue
            
            skip_count = sum(1 for d in decisions if any(
                dec.action.value == "SKIP" for dec in d.decisions
            ))
            skip_rate = skip_count / len(decisions)
            
            if skip_rate >= self.pattern_threshold:
                patterns.append(RecurringPattern(
                    pattern_type="weekly",
                    description=f"{dow} Avoidance Pattern",
                    frequency=skip_rate,
                    confidence=min(0.9, skip_rate + 0.1),
                    examples=[f"Skipped {skip_count}/{len(decisions)} {dow}s"]
                ))
        
        return patterns
    
    def _analyze_stress_patterns(self, history: list) -> list[RecurringPattern]:
        """Detect stress-triggered behavior patterns."""
        patterns = []
        
        high_stress_decisions = [
            d for d in history 
            if d.state_snapshot and d.state_snapshot.get('stress_level', '').upper() == 'HIGH'
        ]
        
        if len(high_stress_decisions) >= 3:
            skip_count = sum(1 for d in high_stress_decisions if any(
                dec.action.value == "SKIP" for dec in d.decisions
            ))
            skip_rate = skip_count / len(high_stress_decisions)
            
            if skip_rate >= 0.5:
                patterns.append(RecurringPattern(
                    pattern_type="situational",
                    description="Stress-Induced Avoidance",
                    frequency=skip_rate,
                    confidence=0.8,
                    examples=[f"Skip rate under stress: {skip_rate:.0%}"]
                ))
        
        return patterns
    
    def _analyze_sleep_cascades(self, history: list) -> list[RecurringPattern]:
        """Detect sleep debt cascade patterns."""
        patterns = []
        
        # Find consecutive low-sleep days
        consecutive_low = 0
        max_consecutive = 0
        
        for decision in history:
            if decision.state_snapshot:
                sleep = decision.state_snapshot.get('sleep_hours', 7)
                if sleep < 6.5:
                    consecutive_low += 1
                    max_consecutive = max(max_consecutive, consecutive_low)
                else:
                    consecutive_low = 0
        
        if max_consecutive >= 3:
            patterns.append(RecurringPattern(
                pattern_type="trigger-based",
                description="Sleep Debt Cascade",
                frequency=max_consecutive / len(history),
                confidence=0.85,
                examples=[f"{max_consecutive} consecutive low-sleep days detected"]
            ))
        
        return patterns
    
    def assess_present_moment(self, history: list, current_state: dict) -> PresentContext:
        """Assess current context relative to past."""
        now = datetime.now()
        dow = now.strftime("%A")
        hour = now.hour
        
        if hour < 12:
            time_of_day = "morning"
        elif hour < 17:
            time_of_day = "afternoon"
        else:
            time_of_day = "evening"
        
        # Find similar past situations
        similar = []
        for decision in history[-14:]:  # Last 2 weeks
            if decision.timestamp.strftime("%A") == dow:
                similar.append({
                    "date": decision.timestamp.strftime("%Y-%m-%d"),
                    "outcome": "skipped" if any(d.action.value == "SKIP" for d in decision.decisions) else "completed"
                })
        
        # Calculate risk level
        risk_factors = []
        risk_score = 0
        
        sleep = current_state.get('sleep_hours', 7)
        if sleep < 6:
            risk_factors.append(f"Critical sleep debt ({sleep}h)")
            risk_score += 3
        elif sleep < 7:
            risk_factors.append(f"Moderate sleep debt ({sleep}h)")
            risk_score += 1
        
        stress = current_state.get('stress_level', 'MODERATE')
        if isinstance(stress, str) and stress.upper() == 'HIGH':
            risk_factors.append("High stress level")
            risk_score += 2
        
        energy = current_state.get('energy_level', 5)
        if energy <= 3:
            risk_factors.append(f"Low energy ({energy}/10)")
            risk_score += 2
        
        if risk_score >= 5:
            risk_level = "critical"
        elif risk_score >= 3:
            risk_level = "high"
        elif risk_score >= 1:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        return PresentContext(
            day_of_week=dow,
            time_of_day=time_of_day,
            similar_past_situations=similar,
            risk_level=risk_level,
            risk_factors=risk_factors
        )
    
    def project_outcomes(
        self, 
        patterns: list[RecurringPattern],
        context: PresentContext,
        current_state: dict
    ) -> list[FutureTrajectory]:
        """Project future outcomes based on current trajectory."""
        trajectories = []
        
        # 24-hour projection
        if context.risk_level in ["high", "critical"]:
            trajectories.append(FutureTrajectory(
                timeline="24h",
                predicted_outcome="Energy crash and decision fatigue",
                probability=0.75,
                impact_level="moderate",
                intervention_window="Next 4 hours"
            ))
        
        # 1-week projection
        sleep = current_state.get('sleep_hours', 7)
        if sleep < 6.5:
            trajectories.append(FutureTrajectory(
                timeline="1 week",
                predicted_outcome="Accumulated sleep debt leading to immune suppression",
                probability=0.65,
                impact_level="major",
                intervention_window="Tonight (prioritize 8h sleep)"
            ))
        
        # Pattern-based projection
        for pattern in patterns:
            if pattern.frequency >= 0.7:
                trajectories.append(FutureTrajectory(
                    timeline="1 month",
                    predicted_outcome=f"Habit collapse due to {pattern.description}",
                    probability=pattern.frequency,
                    impact_level="severe",
                    intervention_window="This week (break the pattern)"
                ))
        
        return trajectories
    
    def _generate_recommendation(
        self,
        patterns: list[RecurringPattern],
        context: PresentContext,
        trajectories: list[FutureTrajectory]
    ) -> str:
        """Generate actionable recommendation."""
        if context.risk_level == "critical":
            return f"⚠️ CRITICAL: {', '.join(context.risk_factors)}. Immediate rest required."
        
        if trajectories and trajectories[0].impact_level in ["major", "severe"]:
            return f"🔮 Pattern Alert: {trajectories[0].predicted_outcome}. {trajectories[0].intervention_window}"
        
        if patterns:
            return f"📊 Detected: {patterns[0].description}. Consider breaking this pattern today."
        
        return "✅ No immediate concerns. Maintain current trajectory."
    
    def _calculate_urgency(
        self,
        context: PresentContext,
        trajectories: list[FutureTrajectory]
    ) -> int:
        """Calculate urgency level (1-5)."""
        if context.risk_level == "critical":
            return 5
        if context.risk_level == "high":
            return 4
        
        if trajectories:
            max_impact = max(
                (t for t in trajectories),
                key=lambda t: {"minor": 1, "moderate": 2, "major": 3, "severe": 4}.get(t.impact_level, 0)
            )
            if max_impact.impact_level == "severe":
                return 4
            if max_impact.impact_level == "major":
                return 3
        
        return 2 if context.risk_level == "moderate" else 1
