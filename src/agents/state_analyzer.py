"""
State Analyzer Agent - Ingests signals and builds health state snapshots.
"""
from datetime import datetime
from typing import Optional

from src.models import HealthState, WearableData, StressLevel, UserProfile
from src.data import CSVDataLoader, HistoryTracker, derive_energy_level, generate_stress_level


class StateAnalyzer:
    """
    Agent that analyzes current health signals and produces a complete
    state snapshot for downstream decision-making.
    
    Responsibilities:
    - Ingest wearable data (CSV or real-time)
    - Derive stress and energy levels
    - Calculate historical context (sleep debt, missed workouts)
    - Produce unified HealthState object
    """
    
    def __init__(self, user_profile: UserProfile):
        self.user_profile = user_profile
        self.history_cache: list[WearableData] = []
    
    def analyze(
        self,
        wearable_data: WearableData,
        time_available_hours: float,
        user_reported_stress: Optional[StressLevel] = None,
        user_reported_energy: Optional[int] = None
    ) -> HealthState:
        """
        Analyze current state and produce a HealthState snapshot.
        
        Args:
            wearable_data: Current day's wearable data
            time_available_hours: User-reported available time
            user_reported_stress: Optional user override for stress
            user_reported_energy: Optional user override for energy (1-10)
        
        Returns:
            Complete HealthState for decision-making
        """
        # Update history cache
        self.history_cache.append(wearable_data)
        
        # Derive stress from wearable if not user-reported
        if user_reported_stress:
            stress = user_reported_stress
        else:
            stress = generate_stress_level(
                wearable_data.hrv_ms,
                wearable_data.resting_heart_rate,
                wearable_data.sleep_hours
            )
        
        # Derive energy from wearable if not user-reported
        if user_reported_energy:
            energy = user_reported_energy
        else:
            energy = derive_energy_level(
                wearable_data.sleep_hours,
                wearable_data.sleep_quality_score,
                wearable_data.hrv_ms
            )
        
        # Calculate historical context
        history_tracker = HistoryTracker(self.history_cache)
        history_summary = history_tracker.get_history_summary(
            target_sleep=self.user_profile.target_sleep_hours
        )
        
        # Build final state
        state = HealthState.from_wearable(
            wearable=wearable_data,
            time_available=time_available_hours,
            stress=stress,
            energy=energy,
            history=history_summary
        )
        
        return state
    
    def analyze_from_csv(
        self,
        csv_path: str,
        time_available_hours: float,
        target_date: Optional[datetime] = None
    ) -> HealthState:
        """
        Load wearable data from CSV and analyze.
        Uses the latest entry if target_date not specified.
        """
        loader = CSVDataLoader(csv_path)
        all_data = loader.load_all()
        
        if not all_data:
            raise ValueError("No data found in CSV")
        
        # Update history cache with all data
        self.history_cache = all_data
        
        # Get target day's data
        if target_date:
            target_data = [d for d in all_data if d.timestamp.date() == target_date.date()]
            if not target_data:
                raise ValueError(f"No data found for {target_date.date()}")
            wearable = target_data[0]
        else:
            # Use latest
            wearable = sorted(all_data, key=lambda x: x.timestamp)[-1]
        
        return self.analyze(wearable, time_available_hours)
    
    def get_trend_analysis(self, days: int = 7) -> dict:
        """
        Analyze trends over recent days.
        Returns insights about sleep, activity, and stress patterns.
        """
        if len(self.history_cache) < 2:
            return {"status": "insufficient_data", "days_available": len(self.history_cache)}
        
        recent = self.history_cache[-days:] if len(self.history_cache) >= days else self.history_cache
        
        # Calculate averages
        avg_sleep = sum(d.sleep_hours for d in recent) / len(recent)
        avg_hrv = sum(d.hrv_ms for d in recent) / len(recent)
        avg_steps = sum(d.steps for d in recent) / len(recent)
        
        # Detect trends
        sleep_trend = self._calculate_trend([d.sleep_hours for d in recent])
        hrv_trend = self._calculate_trend([d.hrv_ms for d in recent])
        
        # Burnout detection
        tracker = HistoryTracker(recent)
        burnout_risk, burnout_reason = tracker.detect_burnout_risk()
        
        return {
            "status": "analyzed",
            "days_analyzed": len(recent),
            "averages": {
                "sleep_hours": round(avg_sleep, 1),
                "hrv_ms": round(avg_hrv, 1),
                "daily_steps": int(avg_steps)
            },
            "trends": {
                "sleep": sleep_trend,
                "hrv": hrv_trend
            },
            "burnout_risk": burnout_risk,
            "burnout_reasoning": burnout_reason
        }
    
    def _calculate_trend(self, values: list[float]) -> str:
        """Simple trend detection."""
        if len(values) < 3:
            return "stable"
        
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        diff_pct = (second_half - first_half) / first_half if first_half > 0 else 0
        
        if diff_pct > 0.1:
            return "improving"
        elif diff_pct < -0.1:
            return "declining"
        else:
            return "stable"
