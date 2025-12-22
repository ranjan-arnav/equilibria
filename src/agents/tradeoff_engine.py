"""
Trade-Off Decision Engine - The core decision-making agent.
Makes autonomous prioritization decisions under constraints.
"""
from datetime import datetime
from typing import Optional

from src.models import (
    HealthState, UserProfile, ActiveConstraints, StressLevel,
    TradeOffDecision, DomainDecision, DecisionAction, HealthDomain,
    PlannedTask, FutureImpact
)


class PriorityMatrix:
    """
    Dynamic priority matrix that adjusts domain weights based on
    current state and constraints.
    """
    
    # Base priorities (should sum to 1.0)
    BASE_PRIORITIES = {
        HealthDomain.RECOVERY: 0.30,
        HealthDomain.NUTRITION: 0.25,
        HealthDomain.FITNESS: 0.25,
        HealthDomain.MINDFULNESS: 0.20
    }
    
    # Constraint modifiers: constraint_name -> {domain: modifier}
    CONSTRAINT_MODIFIERS = {
        "critical_sleep": {
            HealthDomain.RECOVERY: +0.25,
            HealthDomain.FITNESS: -0.20,
            HealthDomain.MINDFULNESS: +0.05
        },
        "low_sleep": {
            HealthDomain.RECOVERY: +0.15,
            HealthDomain.FITNESS: -0.10
        },
        "high_stress": {
            HealthDomain.MINDFULNESS: +0.20,
            HealthDomain.FITNESS: -0.10,
            HealthDomain.RECOVERY: +0.10
        },
        "low_energy": {
            HealthDomain.RECOVERY: +0.10,
            HealthDomain.FITNESS: -0.15
        },
        "critical_energy": {
            HealthDomain.RECOVERY: +0.20,
            HealthDomain.FITNESS: -0.25,
            HealthDomain.MINDFULNESS: +0.10
        },
        "overtraining_risk": {
            HealthDomain.RECOVERY: +0.20,
            HealthDomain.FITNESS: -0.20
        },
        "burnout_warning": {
            HealthDomain.RECOVERY: +0.25,
            HealthDomain.FITNESS: -0.25,
            HealthDomain.MINDFULNESS: +0.15,
            HealthDomain.NUTRITION: -0.10
        },
        "time_limited": {
            # When time is limited, focus on most impactful
            HealthDomain.FITNESS: +0.05  # Quick workout > nothing
        },
        "time_critical": {
            # Minimal time - only essentials
            HealthDomain.NUTRITION: +0.10,  # Must eat
            HealthDomain.FITNESS: -0.15
        }
    }
    
    def calculate_adjusted_priorities(
        self,
        constraints: ActiveConstraints,
        user_preferences: Optional[dict] = None
    ) -> tuple[dict[HealthDomain, float], dict[str, str]]:
        """
        Calculate adjusted priorities based on active constraints.
        
        Returns:
            - Dict of domain -> adjusted priority
            - Dict of adjustment explanations
        """
        priorities = dict(self.BASE_PRIORITIES)
        adjustments = {}
        
        # Apply constraint modifiers
        for constraint in constraints.constraints:
            if constraint.name in self.CONSTRAINT_MODIFIERS:
                modifiers = self.CONSTRAINT_MODIFIERS[constraint.name]
                for domain, modifier in modifiers.items():
                    # Scale modifier by constraint severity
                    scaled_modifier = modifier * constraint.severity
                    priorities[domain] = priorities.get(domain, 0) + scaled_modifier
                    
                    # Track adjustment for transparency
                    sign = "+" if scaled_modifier > 0 else ""
                    adjustments[f"{domain.value}_{constraint.name}"] = (
                        f"{sign}{scaled_modifier:.2f} ({constraint.name})"
                    )
        
        # Apply user preferences if provided
        if user_preferences:
            for domain in HealthDomain:
                pref_key = f"{domain.value}_priority"
                if pref_key in user_preferences:
                    # Blend with user preference (30% user, 70% calculated)
                    user_pref = user_preferences[pref_key]
                    priorities[domain] = priorities[domain] * 0.7 + user_pref * 0.3
        
        # Ensure no negative priorities and normalize
        priorities = {k: max(0.05, v) for k, v in priorities.items()}
        total = sum(priorities.values())
        priorities = {k: v / total for k, v in priorities.items()}
        
        return priorities, adjustments


class TradeOffEngine:
    """
    Core decision-making agent that autonomously prioritizes health
    behaviors under constraints.
    
    This is the heart of the HTPA system - it makes transparent,
    constraint-aware trade-off decisions.
    """
    
    def __init__(self, user_profile: UserProfile):
        self.user_profile = user_profile
        self.priority_matrix = PriorityMatrix()
        self.decision_history: list[TradeOffDecision] = []
    
    def decide(
        self,
        state: HealthState,
        constraints: ActiveConstraints,
        planned_tasks: list[PlannedTask]
    ) -> TradeOffDecision:
        """
        Make a trade-off decision for the current state.
        
        Args:
            state: Current health state snapshot
            constraints: Active constraints from evaluator
            planned_tasks: Originally planned tasks for each domain
            
        Returns:
            TradeOffDecision with full reasoning trail
        """
        decision = TradeOffDecision(
            timestamp=datetime.now(),
            state_snapshot=state.to_dict(),
            constraints_active=constraints.to_list()
        )
        
        # Calculate adjusted priorities
        user_prefs = {
            "fitness_priority": self.user_profile.domain_preferences.fitness_priority,
            "nutrition_priority": self.user_profile.domain_preferences.nutrition_priority,
            "recovery_priority": self.user_profile.domain_preferences.recovery_priority,
            "mindfulness_priority": self.user_profile.domain_preferences.mindfulness_priority
        }
        
        priorities, adjustments = self.priority_matrix.calculate_adjusted_priorities(
            constraints, user_prefs
        )
        decision.priority_adjustments = adjustments
        
        # Sort domains by adjusted priority
        ranked_domains = sorted(priorities.items(), key=lambda x: -x[1])
        
        # Calculate available capacity
        total_planned_time = sum(t.duration_minutes for t in planned_tasks)
        available_time_minutes = state.time_available_hours * 60
        
        # Energy budget (simplified: energy level scales capacity)
        energy_factor = state.energy_level / 10.0
        effective_capacity = available_time_minutes * energy_factor
        
        # Make decisions for each domain
        time_allocated = 0
        for domain, priority in ranked_domains:
            domain_tasks = [t for t in planned_tasks if t.domain == domain]
            
            if not domain_tasks:
                continue
            
            task = domain_tasks[0]  # Take first task for domain
            domain_decision = self._decide_task(
                task=task,
                priority=priority,
                constraints=constraints,
                time_remaining=effective_capacity - time_allocated,
                state=state
            )
            
            if domain_decision.action in [DecisionAction.PRIORITIZE, DecisionAction.MAINTAIN]:
                time_allocated += task.duration_minutes
            elif domain_decision.action == DecisionAction.DOWNGRADE and domain_decision.adjusted_task:
                time_allocated += domain_decision.adjusted_task.duration_minutes
            
            decision.add_decision(domain_decision)
        
        # Determine future impacts
        future_impacts = self._calculate_future_impacts(decision, state, constraints)
        for impact in future_impacts:
            decision.add_future_impact(impact)
        
        # Generate reasoning summary
        decision.reasoning_summary = self._generate_summary(decision, state, constraints)
        decision.confidence_score = self._calculate_confidence(constraints)
        
        # Store in history
        self.decision_history.append(decision)
        
        return decision
    
    def _decide_task(
        self,
        task: PlannedTask,
        priority: float,
        constraints: ActiveConstraints,
        time_remaining: float,
        state: HealthState
    ) -> DomainDecision:
        """Decide what to do with a specific task."""
        
        # Default to maintain
        action = DecisionAction.MAINTAIN
        adjusted_task = None
        reasoning = ""
        
        # Check if we have time
        if time_remaining < task.duration_minutes * 0.5:
            if priority >= 0.3:
                # High priority but no time - aggressive downgrade
                action = DecisionAction.DOWNGRADE
                adjusted_task = self._create_minimal_version(task)
                reasoning = f"Time critically limited but {task.domain.value} is high priority - minimal version"
            else:
                action = DecisionAction.SKIP
                reasoning = f"Insufficient time and {task.domain.value} not highest priority today"
        
        # Check domain-specific rules
        elif task.domain == HealthDomain.FITNESS:
            action, adjusted_task, reasoning = self._decide_fitness(
                task, constraints, state, priority
            )
        
        elif task.domain == HealthDomain.RECOVERY:
            action, adjusted_task, reasoning = self._decide_recovery(
                task, constraints, state, priority
            )
        
        elif task.domain == HealthDomain.MINDFULNESS:
            action, adjusted_task, reasoning = self._decide_mindfulness(
                task, constraints, state, priority
            )
        
        elif task.domain == HealthDomain.NUTRITION:
            action, adjusted_task, reasoning = self._decide_nutrition(
                task, constraints, state, priority
            )
        
        # High priority boost
        if priority >= 0.35 and action == DecisionAction.MAINTAIN:
            action = DecisionAction.PRIORITIZE
            reasoning = f"High adjusted priority ({priority:.2f}) - prioritizing {task.domain.value}"
        
        return DomainDecision(
            domain=task.domain,
            action=action,
            original_task=task,
            adjusted_task=adjusted_task,
            reasoning=reasoning or f"Standard execution of {task.name}",
            priority_score=priority
        )
    
    def _decide_fitness(
        self,
        task: PlannedTask,
        constraints: ActiveConstraints,
        state: HealthState,
        priority: float
    ) -> tuple[DecisionAction, Optional[PlannedTask], str]:
        """Make fitness-specific decision."""
        
        # Critical constraints = skip or heavy downgrade
        if constraints.has("burnout_warning"):
            return (
                DecisionAction.SKIP,
                None,
                "Burnout risk detected - skipping workout to prioritize recovery"
            )
        
        if constraints.has("critical_sleep") or constraints.has("critical_energy"):
            adjusted = PlannedTask(
                domain=HealthDomain.FITNESS,
                name="Light stretching",
                duration_minutes=10,
                intensity=0.2,
                description="Gentle movement only"
            )
            return (
                DecisionAction.DOWNGRADE,
                adjusted,
                "Critical fatigue - replacing with light stretching to maintain movement habit"
            )
        
        if constraints.has("high_stress") and constraints.has("low_sleep"):
            adjusted = PlannedTask(
                domain=HealthDomain.FITNESS,
                name="Recovery walk",
                duration_minutes=20,
                intensity=0.3,
                description="Low-intensity outdoor walk"
            )
            return (
                DecisionAction.DOWNGRADE,
                adjusted,
                "High stress + poor sleep - replacing HIIT with recovery walk"
            )
        
        if constraints.has("overtraining_risk"):
            adjusted = PlannedTask(
                domain=HealthDomain.FITNESS,
                name="Mobility work",
                duration_minutes=15,
                intensity=0.25,
                description="Active recovery mobility"
            )
            return (
                DecisionAction.DOWNGRADE,
                adjusted,
                "Overtraining risk - substituting with mobility work for active recovery"
            )
        
        if constraints.has("low_energy"):
            # Reduce intensity but maintain duration
            adjusted = PlannedTask(
                domain=HealthDomain.FITNESS,
                name=f"{task.name} (reduced intensity)",
                duration_minutes=task.duration_minutes,
                intensity=task.intensity * 0.6,
                description=f"Lower intensity version: {task.description}"
            )
            return (
                DecisionAction.DOWNGRADE,
                adjusted,
                "Low energy - reducing workout intensity by 40%"
            )
        
        return (DecisionAction.MAINTAIN, None, "Conditions favorable for planned workout")
    
    def _decide_recovery(
        self,
        task: PlannedTask,
        constraints: ActiveConstraints,
        state: HealthState,
        priority: float
    ) -> tuple[DecisionAction, Optional[PlannedTask], str]:
        """Make recovery-specific decision."""
        
        # Recovery should almost never be skipped when constraints are active
        if any(constraints.has(c) for c in ["critical_sleep", "burnout_warning", "overtraining_risk"]):
            return (
                DecisionAction.PRIORITIZE,
                None,
                "Recovery critical due to active fatigue/burnout signals"
            )
        
        if constraints.has("time_critical"):
            adjusted = PlannedTask(
                domain=HealthDomain.RECOVERY,
                name="Power nap",
                duration_minutes=20,
                intensity=0.1,
                description="Quick restorative rest"
            )
            return (
                DecisionAction.DOWNGRADE,
                adjusted,
                "Time critical - condensed recovery with power nap"
            )
        
        return (DecisionAction.MAINTAIN, None, "Recovery as planned")
    
    def _decide_mindfulness(
        self,
        task: PlannedTask,
        constraints: ActiveConstraints,
        state: HealthState,
        priority: float
    ) -> tuple[DecisionAction, Optional[PlannedTask], str]:
        """Make mindfulness-specific decision."""
        
        if constraints.has("high_stress"):
            return (
                DecisionAction.PRIORITIZE,
                None,
                "High stress detected - prioritizing mindfulness for stress reduction"
            )
        
        if constraints.has("time_critical"):
            adjusted = PlannedTask(
                domain=HealthDomain.MINDFULNESS,
                name="Breathing exercise",
                duration_minutes=5,
                intensity=0.2,
                description="Quick box breathing"
            )
            return (
                DecisionAction.DOWNGRADE,
                adjusted,
                "Time critical - condensed to 5-minute breathing exercise"
            )
        
        if state.energy_level <= 3:
            # Low energy = good time for meditation
            return (
                DecisionAction.PRIORITIZE,
                None,
                "Low energy state - meditation supports recovery without physical demand"
            )
        
        return (DecisionAction.MAINTAIN, None, "Mindfulness as planned")
    
    def _decide_nutrition(
        self,
        task: PlannedTask,
        constraints: ActiveConstraints,
        state: HealthState,
        priority: float
    ) -> tuple[DecisionAction, Optional[PlannedTask], str]:
        """Make nutrition-specific decision."""
        
        # Nutrition is essential but can be simplified
        if constraints.has("time_critical"):
            adjusted = PlannedTask(
                domain=HealthDomain.NUTRITION,
                name="Simple healthy meal",
                duration_minutes=10,
                intensity=0.1,
                description="Pre-prepared or quick healthy option"
            )
            return (
                DecisionAction.DOWNGRADE,
                adjusted,
                "Time critical - simplify to pre-prepared healthy option rather than cooking"
            )
        
        if constraints.has("low_energy"):
            adjusted = PlannedTask(
                domain=HealthDomain.NUTRITION,
                name="Energy-supportive meal",
                duration_minutes=task.duration_minutes,
                intensity=task.intensity,
                description="Focus on complex carbs and lean protein for energy"
            )
            return (
                DecisionAction.MAINTAIN,
                adjusted,
                "Low energy - adjusting meal focus to energy-supportive nutrients"
            )
        
        return (DecisionAction.MAINTAIN, None, "Nutrition plan as scheduled")
    
    def _create_minimal_version(self, task: PlannedTask) -> PlannedTask:
        """Create absolute minimal version of a task."""
        minimal_durations = {
            HealthDomain.FITNESS: 10,
            HealthDomain.NUTRITION: 5,
            HealthDomain.RECOVERY: 10,
            HealthDomain.MINDFULNESS: 5
        }
        
        return PlannedTask(
            domain=task.domain,
            name=f"Minimal {task.name}",
            duration_minutes=minimal_durations.get(task.domain, 10),
            intensity=0.2,
            description=f"Abbreviated version of: {task.description}"
        )
    
    def _calculate_future_impacts(
        self,
        decision: TradeOffDecision,
        state: HealthState,
        constraints: ActiveConstraints
    ) -> list[FutureImpact]:
        """Calculate impacts on future plans based on today's decisions."""
        impacts = []
        
        # If fitness was skipped/downgraded, adjust future intensity
        fitness_decision = decision.get_decision(HealthDomain.FITNESS)
        if fitness_decision and fitness_decision.action in [DecisionAction.SKIP, DecisionAction.DOWNGRADE]:
            if constraints.has("burnout_warning") or constraints.has("overtraining_risk"):
                impacts.append(FutureImpact(
                    days_affected=3,
                    adjustment_type="intensity_reduction",
                    description="Reducing workout intensity to 60% for the next 3 days"
                ))
            else:
                impacts.append(FutureImpact(
                    days_affected=1,
                    adjustment_type="workout_reschedule",
                    description="Consider adding light activity tomorrow if energy improves"
                ))
        
        # If sleep debt is high, recommend earlier bedtime
        if state.sleep_debt_hours > 4:
            impacts.append(FutureImpact(
                days_affected=2,
                adjustment_type="sleep_extension",
                description=f"Recommend adding 30 min to sleep for 2 nights to address {state.sleep_debt_hours:.1f}h debt"
            ))
        
        # If multiple constraints, suggest deload
        if constraints.has("burnout_warning"):
            impacts.append(FutureImpact(
                days_affected=7,
                adjustment_type="deload_week",
                description="Consider a deload week: reduce all fitness intensity by 50%"
            ))
        
        return impacts
    
    def _generate_summary(
        self,
        decision: TradeOffDecision,
        state: HealthState,
        constraints: ActiveConstraints
    ) -> str:
        """Generate a concise reasoning summary."""
        parts = []
        
        if constraints.constraints:
            parts.append(f"Given {len(constraints.constraints)} active constraints")
        
        prioritized = [d for d in decision.decisions if d.action == DecisionAction.PRIORITIZE]
        if prioritized:
            domains = ", ".join(d.domain.value for d in prioritized)
            parts.append(f"prioritized {domains}")
        
        downgraded = [d for d in decision.decisions if d.action == DecisionAction.DOWNGRADE]
        if downgraded:
            domains = ", ".join(d.domain.value for d in downgraded)
            parts.append(f"downgraded {domains}")
        
        skipped = [d for d in decision.decisions if d.action == DecisionAction.SKIP]
        if skipped:
            domains = ", ".join(d.domain.value for d in skipped)
            parts.append(f"skipped {domains}")
        
        return "; ".join(parts) + "." if parts else "All tasks maintained as planned."
    
    def _calculate_confidence(self, constraints: ActiveConstraints) -> float:
        """Calculate confidence score based on constraint clarity."""
        if not constraints.constraints:
            return 0.95  # High confidence when no constraints
        
        # Lower confidence with more/higher severity constraints
        avg_severity = sum(c.severity for c in constraints.constraints) / len(constraints.constraints)
        return max(0.5, 0.9 - avg_severity * 0.3)
