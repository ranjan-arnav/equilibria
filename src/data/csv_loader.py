"""
CSV Data Loader - Load and parse wearable data from CSV files.
"""
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.models.health_state import WearableData, HealthState, StressLevel
from src.data.synthetic_generator import generate_stress_level, derive_energy_level


class CSVDataLoader:
    """Load wearable data from CSV files."""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
    
    def load_all(self) -> list[WearableData]:
        """Load all rows from CSV as WearableData objects."""
        data = []
        
        with open(self.filepath, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    wearable = WearableData(
                        timestamp=datetime.strptime(row['date'], '%Y-%m-%d'),
                        sleep_hours=float(row['sleep_hours']),
                        deep_sleep_percent=float(row['deep_sleep_pct']),
                        wake_events=int(row['wake_events']),
                        resting_heart_rate=int(row['resting_hr']),
                        hrv_ms=float(row['hrv_ms']),
                        steps=int(row['steps']),
                        active_minutes=int(row['active_minutes']),
                        calories_burned=int(row['calories'])
                    )
                    data.append(wearable)
                except (KeyError, ValueError) as e:
                    print(f"Warning: Skipping row due to error: {e}")
                    continue
        
        return data
    
    def load_latest(self, n: int = 1) -> list[WearableData]:
        """Load the n most recent entries."""
        all_data = self.load_all()
        all_data.sort(key=lambda x: x.timestamp, reverse=True)
        return all_data[:n]
    
    def load_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> list[WearableData]:
        """Load entries within a date range."""
        all_data = self.load_all()
        return [
            d for d in all_data
            if start_date <= d.timestamp <= end_date
        ]
    
    def to_health_state(
        self,
        wearable: WearableData,
        time_available: float,
        history: Optional[dict] = None
    ) -> HealthState:
        """
        Convert wearable data to a complete HealthState.
        Derives stress and energy from wearable signals.
        """
        stress = generate_stress_level(
            wearable.hrv_ms,
            wearable.resting_heart_rate,
            wearable.sleep_hours
        )
        
        energy = derive_energy_level(
            wearable.sleep_hours,
            wearable.sleep_quality_score,
            wearable.hrv_ms
        )
        
        return HealthState.from_wearable(
            wearable=wearable,
            time_available=time_available,
            stress=stress,
            energy=energy,
            history=history
        )


class HistoryTracker:
    """Track historical patterns from wearable data."""
    
    def __init__(self, data: list[WearableData]):
        self.data = sorted(data, key=lambda x: x.timestamp)
    
    def get_sleep_debt(self, target_hours: float = 7.5, days: int = 7) -> float:
        """Calculate accumulated sleep debt over recent days."""
        recent = self.data[-days:] if len(self.data) >= days else self.data
        
        total_debt = 0.0
        for d in recent:
            debt = max(0, target_hours - d.sleep_hours)
            total_debt += debt
        
        return total_debt
    
    def get_missed_workout_estimate(self, target_active_mins: int = 30) -> int:
        """Estimate missed workouts based on low activity days."""
        recent_7 = self.data[-7:] if len(self.data) >= 7 else self.data
        
        return sum(1 for d in recent_7 if d.active_minutes < target_active_mins)
    
    def get_consecutive_high_effort_days(self, steps_threshold: int = 10000) -> int:
        """Count consecutive high-effort days ending today."""
        count = 0
        for d in reversed(self.data):
            if d.steps >= steps_threshold or d.active_minutes >= 45:
                count += 1
            else:
                break
        return count
    
    def get_average_hrv(self, days: int = 7) -> float:
        """Get average HRV for baseline comparison."""
        recent = self.data[-days:] if len(self.data) >= days else self.data
        if not recent:
            return 45.0  # Default baseline
        return sum(d.hrv_ms for d in recent) / len(recent)
    
    def detect_burnout_risk(self) -> tuple[bool, str]:
        """
        Detect if user is at risk of burnout based on patterns.
        Returns (is_at_risk, reasoning)
        """
        if len(self.data) < 5:
            return False, "Insufficient data"
        
        recent_5 = self.data[-5:]
        
        # Check for declining HRV trend
        hrv_trend = [d.hrv_ms for d in recent_5]
        hrv_declining = all(hrv_trend[i] > hrv_trend[i+1] for i in range(len(hrv_trend)-1))
        
        # Check for consistently poor sleep
        avg_sleep = sum(d.sleep_hours for d in recent_5) / 5
        poor_sleep = avg_sleep < 6.0
        
        # Check for elevated resting HR
        avg_hr = sum(d.resting_heart_rate for d in recent_5) / 5
        elevated_hr = avg_hr > 72
        
        if hrv_declining and poor_sleep:
            return True, "Declining HRV combined with insufficient sleep indicates burnout risk"
        elif poor_sleep and elevated_hr:
            return True, "Consistently poor sleep with elevated heart rate suggests overtraining"
        elif hrv_declining and elevated_hr:
            return True, "Declining HRV trend with elevated heart rate indicates stress accumulation"
        
        return False, "No burnout patterns detected"
    
    def get_history_summary(self, target_sleep: float = 7.5) -> dict:
        """Get a summary dict for HealthState creation."""
        return {
            "sleep_debt": self.get_sleep_debt(target_sleep),
            "missed_workouts": self.get_missed_workout_estimate(),
            "high_effort_days": self.get_consecutive_high_effort_days()
        }
