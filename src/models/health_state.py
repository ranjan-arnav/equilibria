"""
Health State Model - Represents the current health snapshot of a user.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class StressLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EnergyLevel(str, Enum):
    DEPLETED = "depleted"  # 1-2
    LOW = "low"            # 3-4
    MODERATE = "moderate"  # 5-6
    HIGH = "high"          # 7-8
    OPTIMAL = "optimal"    # 9-10


@dataclass
class WearableData:
    """Raw wearable metrics from CSV or simulated data."""
    timestamp: datetime
    sleep_hours: float
    deep_sleep_percent: float
    wake_events: int
    resting_heart_rate: int
    hrv_ms: float  # Heart rate variability in milliseconds
    steps: int
    active_minutes: int
    calories_burned: int
    
    @property
    def sleep_quality_score(self) -> float:
        """Calculate sleep quality 0-100 based on duration and quality metrics."""
        duration_score = min(self.sleep_hours / 8.0, 1.0) * 50
        deep_sleep_score = min(self.deep_sleep_percent / 25.0, 1.0) * 30
        wake_penalty = max(0, (5 - self.wake_events) / 5.0) * 20
        return duration_score + deep_sleep_score + wake_penalty


@dataclass
class HealthState:
    """
    Complete health state snapshot combining wearable data with derived insights.
    Used by agents to make trade-off decisions.
    """
    timestamp: datetime
    
    # Core metrics
    sleep_hours: float
    sleep_quality: float  # 0-100
    energy_level: int  # 1-10
    stress_level: StressLevel
    
    # Derived constraints
    time_available_hours: float
    
    # Historical context
    missed_workouts_last_7_days: int = 0
    consecutive_high_effort_days: int = 0
    sleep_debt_hours: float = 0.0  # Accumulated sleep deficit
    
    # Optional wearable details
    hrv_ms: Optional[float] = None
    resting_hr: Optional[int] = None
    steps_today: int = 0
    
    @property
    def readiness_score(self) -> int:
        """
        Calculate professional Readiness Score (0-100).
        Logic:
        - HRV (40%): Higher is better
        - Sleep Quality (30%): From wearable
        - Resting HR (20%): Lower is better
        - Sleep Balance (10%): Based on debt
        """
        # 1. Normalize HRV (20ms-100ms range)
        hrv_val = self.hrv_ms or 40.0
        hrv_score = min(max((hrv_val - 20) / 80.0, 0.0), 1.0) * 100
        
        # 2. Normalize RHR (40bpm-100bpm range, inverted)
        rhr_val = self.resting_hr or 70
        rhr_score = 100 - (min(max((rhr_val - 40) / 60.0, 0.0), 1.0) * 100)
        
        # 3. Sleep Balance (0 debt = 100, >10h debt = 0)
        debt_score = max(0, 100 - (self.sleep_debt_hours * 10))
        
        # Weighted avg
        score = (
            (hrv_score * 0.40) +
            (self.sleep_quality * 0.30) +
            (rhr_score * 0.20) +
            (debt_score * 0.10)
        )
        return int(round(score))
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "sleep_hours": self.sleep_hours,
            "sleep_quality": self.sleep_quality,
            "energy_level": self.energy_level,
            "stress_level": self.stress_level.value,
            "time_available_hours": self.time_available_hours,
            "missed_workouts_7d": self.missed_workouts_last_7_days,
            "consecutive_high_effort": self.consecutive_high_effort_days,
            "sleep_debt_hours": self.sleep_debt_hours,
            "hrv_ms": self.hrv_ms,
            "resting_hr": self.resting_hr,
            "steps_today": self.steps_today,
            "readiness_score": self.readiness_score
        }
    
    @classmethod
    def from_wearable(
        cls,
        wearable: WearableData,
        time_available: float,
        stress: StressLevel,
        energy: int,
        history: Optional[dict] = None
    ) -> "HealthState":
        """Create HealthState from wearable data plus user inputs."""
        history = history or {}
        
        # Calculate sleep debt (assuming 7.5 hours target)
        target_sleep = 7.5
        sleep_debt = max(0, target_sleep - wearable.sleep_hours)
        
        return cls(
            timestamp=wearable.timestamp,
            sleep_hours=wearable.sleep_hours,
            sleep_quality=wearable.sleep_quality_score,
            energy_level=energy,
            stress_level=stress,
            time_available_hours=time_available,
            missed_workouts_last_7_days=history.get("missed_workouts", 0),
            consecutive_high_effort_days=history.get("high_effort_days", 0),
            sleep_debt_hours=history.get("sleep_debt", 0) + sleep_debt,
            hrv_ms=wearable.hrv_ms,
            resting_hr=wearable.resting_heart_rate,
            steps_today=wearable.steps
        )
    
    def get_energy_category(self) -> EnergyLevel:
        """Convert numeric energy to category."""
        if self.energy_level <= 2:
            return EnergyLevel.DEPLETED
        elif self.energy_level <= 4:
            return EnergyLevel.LOW
        elif self.energy_level <= 6:
            return EnergyLevel.MODERATE
        elif self.energy_level <= 8:
            return EnergyLevel.HIGH
        else:
            return EnergyLevel.OPTIMAL


@dataclass
class Constraint:
    """Represents an active constraint limiting full adherence."""
    name: str
    severity: float  # 0.0 to 1.0
    description: str
    source: str  # e.g., "wearable", "user_input", "derived"


@dataclass
class ActiveConstraints:
    """Collection of currently active constraints."""
    constraints: list[Constraint] = field(default_factory=list)
    
    def add(self, name: str, severity: float, description: str, source: str):
        self.constraints.append(Constraint(name, severity, description, source))
    
    def has(self, name: str) -> bool:
        return any(c.name == name for c in self.constraints)
    
    def get_severity(self, name: str) -> float:
        for c in self.constraints:
            if c.name == name:
                return c.severity
        return 0.0
    
    def to_list(self) -> list[str]:
        return [c.name for c in self.constraints]
    
    def to_dict(self) -> list[dict]:
        return [
            {
                "name": c.name,
                "severity": c.severity,
                "description": c.description,
                "source": c.source
            }
            for c in self.constraints
        ]
