"""
Predictive Engine - Advanced logic for health forecasting and recommendations.
"""
from dataclasses import dataclass
from typing import Optional, List, Tuple
from enum import Enum
import random  # For simulation elements where real historical data is missing
from src.models.health_state import HealthState, EnergyLevel, StressLevel

class BurnoutRisk(str, Enum):
    LOW = "Low Risk"
    MODERATE = "Moderate Risk"
    HIGH = "High Risk"
    CRITICAL = "Critical"

@dataclass
class Recommendation:
    activity_type: str
    intensity: str
    duration_minutes: int
    reasoning: str

class ReadinessForecaster:
    """Predicts future readiness based on trends."""
    
    @staticmethod
    def predict_tomorrow(current_state: HealthState) -> int:
        """
        Predict tomorrow's readiness score using a weighted heuristic.
        In a real ML system, this would use a regression model on history.
        """
        base_score = current_state.readiness_score
        
        # Trend factors
        recovery_bonus = 0
        if current_state.stress_level == StressLevel.LOW:
            recovery_bonus += 5
        elif current_state.stress_level == StressLevel.HIGH:
            recovery_bonus -= 10
            
        if current_state.sleep_debt_hours > 5:
            recovery_bonus -= 5
        elif current_state.sleep_debt_hours == 0:
            recovery_bonus += 5
            
        # Regression to mean adjustment
        predicted = base_score + recovery_bonus
        
        # Clamp 0-100
        return max(0, min(100, int(predicted)))

class WorkloadRecommender:
    """Adaptive workout recommender based on Energy/Stress mapping."""
    
    @staticmethod
    def get_recommendation(state: HealthState) -> Recommendation:
        energy = state.energy_level
        stress = state.stress_level
        
        # Decision Tree Logic
        if stress == StressLevel.HIGH:
            if energy >= 7:
                return Recommendation(
                    activity_type="Boxing / HIIT (Stress Release)",
                    intensity="High",
                    duration_minutes=30,
                    reasoning="High energy allows for intense outlet to release stress."
                )
            elif energy >= 4:
                return Recommendation(
                    activity_type="Strength Training (Controlled)",
                    intensity="Moderate",
                    duration_minutes=45,
                    reasoning="Moderate energy best suited for controlled lifting, avoiding burnout."
                )
            else:
                return Recommendation(
                    activity_type="Yoga / Deep Stretching",
                    intensity="Low",
                    duration_minutes=30,
                    reasoning="High stress and low energy requires active recovery to reset nervous system."
                )
                
        elif stress == StressLevel.MEDIUM:
            if energy >= 6:
                return Recommendation(
                    activity_type="Threshold Run / Cycle",
                    intensity="High",
                    duration_minutes=45,
                    reasoning="Good capacity for cardiovascular strain."
                )
            else:
                return Recommendation(
                    activity_type="Zone 2 Cardio",
                    intensity="Low-Moderate",
                    duration_minutes=60,
                    reasoning="Building aerobic base without overtaxing recovery."
                )
                
        else: # LOW Stress
            if energy >= 8:
                return Recommendation(
                    activity_type="Sprint Intervals / Max Effort",
                    intensity="Max",
                    duration_minutes=40,
                    reasoning="Prime conditions for max effort and PR attempts."
                )
            elif energy >= 5:
                return Recommendation(
                    activity_type="Hypertrophy Lifting",
                    intensity="Moderate-High",
                    duration_minutes=60,
                    reasoning="Ideal state for volume training."
                )
            else:
                return Recommendation(
                    activity_type="Mobility Flow",
                    intensity="Low",
                    duration_minutes=20,
                    reasoning="Low stress but low energy suggests a rest or mobility day."
                )

class BurnoutClassifier:
    """Classifies burnout risk based on cumulative load metrics."""
    
    @staticmethod
    def assess_risk(state: HealthState) -> Tuple[BurnoutRisk, str]:
        score = 0
        reasons = []
        
        # Factor 1: Sleep Debt (High impact)
        if state.sleep_debt_hours > 8:
            score += 3
            reasons.append(f"High sleep debt ({state.sleep_debt_hours:.1f}h)")
        elif state.sleep_debt_hours > 4:
            score += 1
            reasons.append("Moderate sleep debt")
            
        # Factor 2: Chronic Stress
        if state.stress_level == StressLevel.HIGH:
            score += 2
            reasons.append("High acute stress")
            
        # Factor 3: Recent Load (Simulated via consecutive high effort days)
        if state.consecutive_high_effort_days >= 3:
            score += 2
            reasons.append(f"{state.consecutive_high_effort_days} consecutive high efforts")
            
        # Classification
        if score >= 5:
            return BurnoutRisk.CRITICAL, ", ".join(reasons)
        elif score >= 3:
            return BurnoutRisk.HIGH, ", ".join(reasons)
        elif score >= 1:
            return BurnoutRisk.MODERATE, ", ".join(reasons)
        else:
            return BurnoutRisk.LOW, "Balanced metrics"

class FutureSelfAgent:
    """
    Generates a narrative from the user's 'Future Self' (7 days later).
    Uses a lightweight projection engine to forecast the trajectory.
    """
    
    @staticmethod
    def project_trajectory(current_state: HealthState) -> Tuple[HealthState, str]:
        """
        Project state 7 days into the future based on current inertia.
        Returns: (FutureState, PrimaryIssue)
        """
        # 1. Project Sleep Debt
        # If current sleep < 7, debt accumulates. If > 7.5, debt pays down.
        daily_deficit = 7.5 - current_state.sleep_hours
        projected_debt = max(0, current_state.sleep_debt_hours + (daily_deficit * 7))
        
        # 2. Project Burnout (Stress + Energy drain)
        # If Stress is High, Energy drains.
        projected_energy = current_state.energy_level
        if current_state.stress_level == StressLevel.HIGH:
            projected_energy = max(1, projected_energy - 3)
        elif current_state.stress_level == StressLevel.MEDIUM and daily_deficit > 0:
            projected_energy = max(1, projected_energy - 1)
        
        # 3. Identify Primary Issue
        issue = "stable"
        if projected_debt > 15:
            issue = "critical_sleep_debt"
        elif projected_energy <= 2:
            issue = "burnout_crash"
        elif current_state.stress_level == StressLevel.HIGH and projected_debt > 5:
            issue = "wired_and_tired"
        elif projected_energy >= 8 and projected_debt < 2:
            issue = "peak_performance"
            
        return projected_debt, projected_energy, issue

    @staticmethod
    def generate_message(current_state: HealthState) -> Tuple[str, str]:
        """Generate a message from the future."""
        debt, energy, issue = FutureSelfAgent.project_trajectory(current_state)
        
        messages = {
            "critical_sleep_debt": [
                ("📉 Integrity Failure", f"It's me from next Sunday. Look, we hit a wall. That {debt:.1f} hours of sleep debt caught up with us. I can barely focus to write this. Please, go to bed early tonight."),
                ("⚠️ System Collapse", "Hey. We crashed hard on Thursday. Total system restart required. Don't push it today, or we pay for it all week."),
            ],
            "burnout_crash": [
                ("🔥 Burnout Warning", "I'm writing this from the couch because we literally can't move. High stress plus no recovery destroyed us. Cancel the high intensity stuff, okay?"),
                ("🛑 Energy Depleted", "We have zero energy left in the tank by Friday. You need to pull the brakes NOW."),
            ],
            "wired_and_tired": [
                ("⚡ Wired & Tired", "We are vibrating with anxiety but too tired to work. It's a horrible state. Do some breathwork today, please."),
                ("🌀 Spiral Detected", "The stress compounded. We snapped at everyone on Wednesday. Manage the cortisol today."),
            ],
            "peak_performance": [
                ("🚀 All Systems Go", "We crushed it this week! Energy is sky high. Whatever you're doing, keep doing it. We feel amazing."),
                ("⭐ Peak State", "Next Sunday here. We just set a PR. This balance is working perfectly."),
            ],
            "stable": [
                ("✅ Steady Course", "Hey, checking in from Sunday. We made it through fine. Nothing crazy, just solid consistent progress."),
                ("⚓ Holding Steady", "Smooth sailing this week. Good job keeping the balance."),
            ]
        }
        
        candidates = messages.get(issue, messages["stable"])
        return random.choice(candidates)
