"""
Burnout Predictor Agent - Forecasts crisis events before they happen.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from src.models import TradeOffDecision, StressLevel


@dataclass
class BurnoutForecast:
    """Prediction of burnout risk."""
    risk_score: int  # 0-100
    days_to_crisis: Optional[int]  # Estimated days until burnout
    primary_factors: list[str]  # What's driving the risk
    intervention_needed: bool
    severity: str  # "low", "moderate", "high", "critical"


class BurnoutPredictor:
    """Analyzes behavioral trends to predict burnout."""
    
    # Risk thresholds
    CRITICAL_THRESHOLD = 70
    HIGH_THRESHOLD = 50
    MODERATE_THRESHOLD = 30
    
    def __init__(self):
        self.last_forecast: Optional[BurnoutForecast] = None
    
    def analyze(self, decision_history: list[TradeOffDecision]) -> BurnoutForecast:
        """
        Analyze decision history and predict burnout risk.
        
        Args:
            decision_history: Recent decisions (ideally last 7 days)
            
        Returns:
            BurnoutForecast with risk assessment
        """
        if not decision_history:
            return self._create_low_risk_forecast()
        
        # Get last 7 days only
        recent_decisions = self._get_recent_decisions(decision_history, days=7)
        
        if len(recent_decisions) < 2:
            return self._create_low_risk_forecast()
        
        # Calculate individual risk factors
        sleep_risk = self._calculate_sleep_risk(recent_decisions)
        stress_risk = self._calculate_stress_risk(recent_decisions)
        recovery_risk = self._calculate_recovery_risk(recent_decisions)
        energy_risk = self._calculate_energy_decline_risk(recent_decisions)
        
        # Weighted composite score
        risk_score = int(
            sleep_risk * 0.35 +
            stress_risk * 0.30 +
            recovery_risk * 0.20 +
            energy_risk * 0.15
        )
        
        # Identify primary factors
        factors = []
        if sleep_risk > 60:
            factors.append("Sleep debt accumulation")
        if stress_risk > 60:
            factors.append("Chronic stress pattern")
        if recovery_risk > 60:
            factors.append("Insufficient recovery")
        if energy_risk > 60:
            factors.append("Rapid energy decline")
        
        # Estimate days to crisis
        days_to_crisis = self._estimate_crisis_timeline(risk_score, recent_decisions)
        
        # Determine severity
        if risk_score >= self.CRITICAL_THRESHOLD:
            severity = "critical"
        elif risk_score >= self.HIGH_THRESHOLD:
            severity = "high"
        elif risk_score >= self.MODERATE_THRESHOLD:
            severity = "moderate"
        else:
            severity = "low"
        
        forecast = BurnoutForecast(
            risk_score=risk_score,
            days_to_crisis=days_to_crisis,
            primary_factors=factors if factors else ["No significant risk factors"],
            intervention_needed=risk_score >= self.CRITICAL_THRESHOLD,
            severity=severity
        )
        
        self.last_forecast = forecast
        return forecast
    
    def _get_recent_decisions(self, decisions: list[TradeOffDecision], days: int) -> list[TradeOffDecision]:
        """Filter decisions to last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        return [d for d in decisions if d.timestamp >= cutoff]
    
    def _calculate_sleep_risk(self, decisions: list[TradeOffDecision]) -> float:
        """Calculate risk from sleep patterns (0-100)."""
        sleep_hours = []
        
        for decision in decisions:
            if decision.state_snapshot and 'sleep_hours' in decision.state_snapshot:
                sleep_hours.append(decision.state_snapshot['sleep_hours'])
        
        if not sleep_hours:
            return 0
        
        # Check for sleep debt
        avg_sleep = sum(sleep_hours) / len(sleep_hours)
        consecutive_low = 0
        max_consecutive_low = 0
        
        for hours in sleep_hours:
            if hours < 6:
                consecutive_low += 1
                max_consecutive_low = max(max_consecutive_low, consecutive_low)
            else:
                consecutive_low = 0
        
        # Risk factors
        risk = 0
        if avg_sleep < 6.5:
            risk += 40
        elif avg_sleep < 7:
            risk += 20
        
        if max_consecutive_low >= 3:
            risk += 50
        elif max_consecutive_low >= 2:
            risk += 30
        
        return min(100, risk)
    
    def _calculate_stress_risk(self, decisions: list[TradeOffDecision]) -> float:
        """Calculate risk from stress patterns (0-100)."""
        stress_levels = []
        
        for decision in decisions:
            if decision.state_snapshot and 'stress_level' in decision.state_snapshot:
                level = decision.state_snapshot['stress_level']
                # Convert to numeric (handle both enum and string)
                if isinstance(level, str):
                    level_str = level.upper()
                    if level_str == 'HIGH':
                        stress_levels.append(3)
                    elif level_str == 'MODERATE':
                        stress_levels.append(2)
                    else:
                        stress_levels.append(1)
                else:
                    if level == StressLevel.HIGH:
                        stress_levels.append(3)
                    elif level == StressLevel.MODERATE:
                        stress_levels.append(2)
                    else:
                        stress_levels.append(1)
        
        if not stress_levels:
            return 0
        
        # Check for sustained high stress
        consecutive_high = 0
        max_consecutive_high = 0
        
        for level in stress_levels:
            if level >= 3:
                consecutive_high += 1
                max_consecutive_high = max(max_consecutive_high, consecutive_high)
            else:
                consecutive_high = 0
        
        avg_stress = sum(stress_levels) / len(stress_levels)
        
        risk = 0
        if avg_stress >= 2.5:
            risk += 40
        
        if max_consecutive_high >= 3:
            risk += 60
        elif max_consecutive_high >= 2:
            risk += 30
        
        return min(100, risk)
    
    def _calculate_recovery_risk(self, decisions: list[TradeOffDecision]) -> float:
        """Calculate risk from skipped recovery activities (0-100)."""
        recovery_activities = ["Mindfulness", "Sleep", "Recovery"]
        skipped_count = 0
        total_recovery_opportunities = 0
        
        for decision in decisions:
            for domain_decision in decision.decisions:
                domain_name = domain_decision.domain.value
                if any(rec in domain_name for rec in recovery_activities):
                    total_recovery_opportunities += 1
                    if domain_decision.action.value == "SKIP":
                        skipped_count += 1
        
        if total_recovery_opportunities == 0:
            return 0
        
        skip_rate = skipped_count / total_recovery_opportunities
        
        if skip_rate >= 0.6:
            return 80
        elif skip_rate >= 0.4:
            return 50
        elif skip_rate >= 0.2:
            return 25
        
        return 0
    
    def _calculate_energy_decline_risk(self, decisions: list[TradeOffDecision]) -> float:
        """Calculate risk from rapid energy decline (0-100)."""
        energy_levels = []
        
        for decision in decisions:
            if decision.state_snapshot and 'energy_level' in decision.state_snapshot:
                energy_levels.append(decision.state_snapshot['energy_level'])
        
        if len(energy_levels) < 3:
            return 0
        
        # Calculate velocity (change per day)
        changes = []
        for i in range(1, len(energy_levels)):
            changes.append(energy_levels[i] - energy_levels[i-1])
        
        avg_change = sum(changes) / len(changes)
        
        # Declining energy is risky
        if avg_change <= -2:
            return 70
        elif avg_change <= -1:
            return 40
        elif avg_change < 0:
            return 20
        
        return 0
    
    def _estimate_crisis_timeline(self, risk_score: int, decisions: list[TradeOffDecision]) -> Optional[int]:
        """Estimate days until crisis based on current trajectory."""
        if risk_score < self.MODERATE_THRESHOLD:
            return None
        
        # Simple heuristic based on risk score
        if risk_score >= 90:
            return 1
        elif risk_score >= 80:
            return 2
        elif risk_score >= 70:
            return 3
        elif risk_score >= 60:
            return 5
        else:
            return 7
    
    def _create_low_risk_forecast(self) -> BurnoutForecast:
        """Create a default low-risk forecast."""
        return BurnoutForecast(
            risk_score=10,
            days_to_crisis=None,
            primary_factors=["Insufficient data for analysis"],
            intervention_needed=False,
            severity="low"
        )
