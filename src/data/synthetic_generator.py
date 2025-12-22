"""
Synthetic Wearable Data Generator - Creates realistic health data for testing.
"""
import random
from datetime import datetime, timedelta
from typing import Optional
import csv
import os

from src.models.health_state import WearableData, StressLevel


class SyntheticDataGenerator:
    """
    Generates realistic synthetic wearable and health data.
    Supports creating patterns like:
    - Gradual fatigue buildup
    - Weekend recovery
    - Stress spikes
    - Sleep debt accumulation
    """
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
        
        # Baseline parameters (can be customized per user)
        self.baseline_sleep = 7.0
        self.baseline_deep_sleep_pct = 20.0
        self.baseline_resting_hr = 65
        self.baseline_hrv = 45.0
        self.baseline_steps = 8000
    
    def generate_wearable_data(
        self,
        date: datetime,
        fatigue_factor: float = 0.0,  # 0-1, higher = more tired
        stress_factor: float = 0.0,    # 0-1, higher = more stressed
        is_weekend: bool = False
    ) -> WearableData:
        """Generate a single day of wearable data."""
        
        # Sleep varies with fatigue and weekend
        sleep_base = self.baseline_sleep + (0.5 if is_weekend else 0)
        sleep_hours = max(3.0, sleep_base - (fatigue_factor * 2) + random.gauss(0, 0.5))
        
        # Deep sleep decreases with stress
        deep_sleep = max(5, self.baseline_deep_sleep_pct - (stress_factor * 10) + random.gauss(0, 3))
        
        # Wake events increase with stress
        wake_events = int(max(0, stress_factor * 5 + random.gauss(0, 1)))
        
        # HR increases with stress/fatigue
        resting_hr = int(self.baseline_resting_hr + (stress_factor * 10) + (fatigue_factor * 5) + random.gauss(0, 3))
        
        # HRV decreases with stress (inverse relationship)
        hrv = max(15, self.baseline_hrv - (stress_factor * 15) - (fatigue_factor * 10) + random.gauss(0, 5))
        
        # Steps vary - lower when fatigued
        steps = int(max(1000, self.baseline_steps * (1 - fatigue_factor * 0.4) + random.gauss(0, 1000)))
        
        # Active minutes correlate with steps
        active_minutes = int(steps / 150 + random.gauss(0, 10))
        
        # Calories 
        calories = int(1800 + active_minutes * 5 + random.gauss(0, 100))
        
        return WearableData(
            timestamp=date,
            sleep_hours=round(sleep_hours, 1),
            deep_sleep_percent=round(deep_sleep, 1),
            wake_events=wake_events,
            resting_heart_rate=resting_hr,
            hrv_ms=round(hrv, 1),
            steps=steps,
            active_minutes=max(0, active_minutes),
            calories_burned=calories
        )
    
    def generate_week(
        self,
        start_date: Optional[datetime] = None,
        scenario: str = "normal"
    ) -> list[WearableData]:
        """
        Generate a week of data with a specific scenario.
        
        Scenarios:
        - normal: Regular variation
        - burnout: Increasing fatigue over the week
        - recovery: Improving metrics
        - high_stress: Elevated stress throughout
        - weekend_warrior: Low weekdays, active weekends
        """
        start = start_date or datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        data = []
        
        for day in range(7):
            current_date = start + timedelta(days=day)
            is_weekend = day >= 5
            
            if scenario == "burnout":
                fatigue = min(0.9, day * 0.12)  # Builds up
                stress = min(0.8, day * 0.1)
            elif scenario == "recovery":
                fatigue = max(0.1, 0.6 - day * 0.08)  # Decreases
                stress = max(0.1, 0.5 - day * 0.06)
            elif scenario == "high_stress":
                fatigue = 0.3 + random.random() * 0.2
                stress = 0.6 + random.random() * 0.2
            elif scenario == "weekend_warrior":
                if is_weekend:
                    fatigue = 0.1
                    stress = 0.1
                else:
                    fatigue = 0.4
                    stress = 0.5
            else:  # normal
                fatigue = random.random() * 0.4
                stress = random.random() * 0.4
            
            data.append(self.generate_wearable_data(
                current_date, fatigue, stress, is_weekend
            ))
        
        return data
    
    def generate_csv(
        self,
        filepath: str,
        days: int = 30,
        scenario: str = "mixed"
    ):
        """Generate CSV file with wearable data."""
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        
        start = datetime.now().replace(hour=8, minute=0) - timedelta(days=days)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'date', 'sleep_hours', 'deep_sleep_pct', 'wake_events',
                'resting_hr', 'hrv_ms', 'steps', 'active_minutes', 'calories'
            ])
            
            for day in range(days):
                current_date = start + timedelta(days=day)
                is_weekend = current_date.weekday() >= 5
                
                # Create mixed scenarios over the month
                if scenario == "mixed":
                    week_num = day // 7
                    if week_num == 0:
                        fatigue, stress = 0.2, 0.2  # Good week
                    elif week_num == 1:
                        fatigue, stress = 0.4 + (day % 7) * 0.05, 0.5  # Building stress
                    elif week_num == 2:
                        fatigue, stress = 0.6, 0.7  # High stress week
                    else:
                        fatigue, stress = 0.3, 0.3  # Recovery
                else:
                    fatigue = random.random() * 0.5
                    stress = random.random() * 0.5
                
                data = self.generate_wearable_data(current_date, fatigue, stress, is_weekend)
                
                writer.writerow([
                    data.timestamp.strftime('%Y-%m-%d'),
                    data.sleep_hours,
                    data.deep_sleep_percent,
                    data.wake_events,
                    data.resting_heart_rate,
                    data.hrv_ms,
                    data.steps,
                    data.active_minutes,
                    data.calories_burned
                ])
        
        print(f"Generated {days} days of data to {filepath}")


def generate_stress_level(hrv: float, resting_hr: int, sleep_hours: float) -> StressLevel:
    """Derive stress level from wearable signals."""
    stress_score = 0
    
    # Low HRV indicates stress
    if hrv < 30:
        stress_score += 2
    elif hrv < 40:
        stress_score += 1
    
    # Elevated HR indicates stress
    if resting_hr > 75:
        stress_score += 2
    elif resting_hr > 70:
        stress_score += 1
    
    # Poor sleep correlates with stress
    if sleep_hours < 5:
        stress_score += 2
    elif sleep_hours < 6:
        stress_score += 1
    
    if stress_score >= 4:
        return StressLevel.HIGH
    elif stress_score >= 2:
        return StressLevel.MEDIUM
    else:
        return StressLevel.LOW


def derive_energy_level(sleep_hours: float, sleep_quality: float, hrv: float) -> int:
    """Derive energy level (1-10) from wearable data."""
    # Base from sleep
    energy = (sleep_hours / 8.0) * 5  # Up to 5 points from sleep duration
    
    # Add from quality
    energy += (sleep_quality / 100) * 3  # Up to 3 points from quality
    
    # HRV bonus
    if hrv > 50:
        energy += 1.5
    elif hrv > 40:
        energy += 1
    elif hrv < 25:
        energy -= 1
    
    return max(1, min(10, int(round(energy))))


if __name__ == "__main__":
    # Generate sample data
    generator = SyntheticDataGenerator(seed=42)
    generator.generate_csv("data/sample_wearable.csv", days=30, scenario="mixed")
    
    # Also generate specific scenario files
    for scenario in ["burnout", "high_stress", "recovery"]:
        week_data = generator.generate_week(scenario=scenario)
        filepath = f"data/scenario_{scenario}.csv"
        os.makedirs("data", exist_ok=True)
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'sleep_hours', 'deep_sleep_pct', 'wake_events', 
                           'resting_hr', 'hrv_ms', 'steps', 'active_minutes', 'calories'])
            for d in week_data:
                writer.writerow([
                    d.timestamp.strftime('%Y-%m-%d'), d.sleep_hours, d.deep_sleep_percent,
                    d.wake_events, d.resting_heart_rate, d.hrv_ms, d.steps,
                    d.active_minutes, d.calories_burned
                ])
        print(f"Generated {scenario} scenario to {filepath}")
