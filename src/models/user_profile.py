"""
User Profile Model - Represents user goals, preferences, and history.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class FitnessGoal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    ENDURANCE = "endurance"
    GENERAL_FITNESS = "general_fitness"
    STRESS_REDUCTION = "stress_reduction"
    ENERGY_OPTIMIZATION = "energy_optimization"


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


@dataclass
class DomainPreferences:
    """User preferences for each health domain."""
    fitness_priority: float = 0.25  # 0-1
    nutrition_priority: float = 0.25
    recovery_priority: float = 0.25
    mindfulness_priority: float = 0.25
    
    # Flexibility - how willing to skip/downgrade
    fitness_flexibility: float = 0.5  # 0=never skip, 1=very flexible
    nutrition_flexibility: float = 0.3
    recovery_flexibility: float = 0.2  # Usually less flexible on sleep
    mindfulness_flexibility: float = 0.6
    
    def normalize(self):
        """Ensure priorities sum to 1.0"""
        total = (self.fitness_priority + self.nutrition_priority + 
                 self.recovery_priority + self.mindfulness_priority)
        if total > 0:
            self.fitness_priority /= total
            self.nutrition_priority /= total
            self.recovery_priority /= total
            self.mindfulness_priority /= total


@dataclass
class WeeklySchedule:
    """User's typical weekly availability."""
    # Hours available per day (index 0 = Monday)
    available_hours: list[float] = field(
        default_factory=lambda: [2.0, 2.0, 2.0, 2.0, 2.0, 3.0, 3.0]
    )
    
    # Preferred workout days
    workout_days: list[int] = field(default_factory=lambda: [0, 2, 4])  # Mon, Wed, Fri
    
    # High-stress days (e.g., big meetings)
    high_stress_days: list[int] = field(default_factory=list)


@dataclass
class UserProfile:
    """
    Complete user profile including goals, preferences, and constraints.
    """
    user_id: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    
    # Demographics (optional, for personalization)
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    
    # Goals
    primary_goal: FitnessGoal = FitnessGoal.GENERAL_FITNESS
    secondary_goals: list[FitnessGoal] = field(default_factory=list)
    
    # Activity baseline
    activity_level: ActivityLevel = ActivityLevel.MODERATELY_ACTIVE
    
    # Preferences
    domain_preferences: DomainPreferences = field(default_factory=DomainPreferences)
    weekly_schedule: WeeklySchedule = field(default_factory=WeeklySchedule)
    
    # Thresholds for agent decisions
    min_sleep_hours: float = 6.0
    target_sleep_hours: float = 7.5
    max_consecutive_high_effort_days: int = 3
    burnout_prevention_enabled: bool = True
    
    # Adaptation settings
    allow_automatic_adjustments: bool = True
    adjustment_aggressiveness: float = 0.5  # 0=conservative, 1=aggressive
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "primary_goal": self.primary_goal.value,
            "activity_level": self.activity_level.value,
            "domain_preferences": {
                "fitness": self.domain_preferences.fitness_priority,
                "nutrition": self.domain_preferences.nutrition_priority,
                "recovery": self.domain_preferences.recovery_priority,
                "mindfulness": self.domain_preferences.mindfulness_priority
            },
            "thresholds": {
                "min_sleep": self.min_sleep_hours,
                "target_sleep": self.target_sleep_hours,
                "max_high_effort_days": self.max_consecutive_high_effort_days
            }
        }
    
    @classmethod
    def create_default(cls, user_id: str = "default", name: str = "User") -> "UserProfile":
        """Create a default user profile for testing."""
        return cls(
            user_id=user_id,
            name=name,
            age=30,
            primary_goal=FitnessGoal.GENERAL_FITNESS,
            domain_preferences=DomainPreferences()
        )
