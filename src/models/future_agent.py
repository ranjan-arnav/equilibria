
"""
Future Agent - Logic for generating messages from the future.
Isolated to prevent circular imports or caching issues.
"""
from typing import Tuple, Optional
import random
from src.models.health_state import HealthState, StressLevel

class FutureSelfAgent:
    """
    Generates a narrative from the user's 'Future Self' (7 days later).
    Uses a lightweight projection engine to forecast the trajectory.
    """
    
    @staticmethod
    def project_trajectory(current_state: HealthState) -> Tuple[float, int, str]:
        """
        Project state 7 days into the future based on current inertia.
        Returns: (FutureDebt, FutureEnergy, PrimaryIssue)
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
