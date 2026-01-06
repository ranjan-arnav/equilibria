"""
LLM Reasoning Generator - Uses Groq API to generate natural language explanations.
"""
import os
from typing import Optional
from dataclasses import dataclass

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None


@dataclass
class LLMConfig:
    """Configuration for LLM integration."""
    api_key: str
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7
    max_tokens: int = 500


class LLMReasoningGenerator:
    """
    Generates natural language explanations for trade-off decisions
    using Groq's LLM API.
    """
    
    SYSTEM_PROMPT = """You are an empathetic health coach AI that explains trade-off decisions 
to users in a supportive, understanding way. Your explanations should:

1. Acknowledge the user's current state (fatigue, stress, etc.)
2. Explain WHY certain activities were prioritized or skipped
3. Frame trade-offs positively - as smart choices, not failures
4. Be concise but warm (2-3 sentences max per decision)
5. End with encouragement about the future plan

Never use clinical/medical terminology. Be conversational and supportive."""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config
        self.client = None
        
        if config and GROQ_AVAILABLE:
            self.client = Groq(api_key=config.api_key)
        elif not GROQ_AVAILABLE:
            print("Warning: groq package not installed. Using template-based explanations.")
    
    @classmethod
    def from_env(cls) -> "LLMReasoningGenerator":
        """Create generator from environment variables."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return cls(config=None)
        
        config = LLMConfig(
            api_key=api_key,
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        )
        return cls(config)
    
    def generate_explanation(
        self,
        decision_summary: dict,
        state_snapshot: dict,
        constraints: list[str]
    ) -> dict:
        """
        Generate a structured explanation including temporal & context analysis.
        Returns a dict with: explanation, temporal_analysis, context_assessment.
        """
        if not self.client:
            return self._template_explanation(decision_summary, state_snapshot, constraints)
        
        try:
            return self._llm_explanation(decision_summary, state_snapshot, constraints)
        except Exception as e:
            print(f"LLM error: {e}. Falling back to template.")
            return self._template_explanation(decision_summary, state_snapshot, constraints)
    
    def _llm_explanation(
        self,
        decision_summary: dict,
        state_snapshot: dict,
        constraints: list[str]
    ) -> dict:
        """Generate structured explanation using Groq LLM."""
        user_prompt = f"""Analyze the following health decision context:

**State:** Sleep:{state_snapshot.get('sleep_hours')}h, Energy:{state_snapshot.get('energy_level')}/10, Stress:{state_snapshot.get('stress_level')}
**Constraints:** {', '.join(constraints) if constraints else 'None'}
**Decisions:** {self._format_decisions(decision_summary.get('decisions', []))}

Provide a JSON response with:
1. "explanation": 3-4 sentence warm, supportive logic for the decision.
2. "temporal_analysis": Check urgency/timing. (e.g., "Urgency: Low. Recommendation: No immediate concerns.")
3. "context_assessment": Assess risk/environment. (e.g., "Risk Level: Low. Optimal time for recovery.")

Output valid JSON ONLY."""

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": "You are a health analysis engine. Output only valid JSON."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=600,
            response_format={"type": "json_object"}
        )
        
        import json
        content = response.choices[0].message.content
        return json.loads(content)
    
    def _template_explanation(
        self,
        decision_summary: dict,
        state_snapshot: dict,
        constraints: list[str]
    ) -> dict:
        """Generate template-based explanation when LLM unavailable."""
        parts = []
        
        # Acknowledge state
        sleep = state_snapshot.get('sleep_hours', 7)
        energy = state_snapshot.get('energy_level', 5)
        stress = state_snapshot.get('stress_level', 'medium')
        
        if sleep < 6 or energy < 4:
            parts.append("I can see you're running on low reserves today.")
        elif stress == 'high':
            parts.append("It looks like stress is weighing on you today.")
        else:
            parts.append("Based on your current state,")
        
        # Summarize key decisions
        decisions = decision_summary.get('decisions', [])
        prioritized = [d for d in decisions if d.get('action') == 'PRIORITIZE']
        skipped = [d for d in decisions if d.get('action') == 'SKIP']
        
        if prioritized:
            domains = [d['domain'] for d in prioritized]
            parts.append(f"I've prioritized {', '.join(domains)} to give you the biggest benefit.")
        
        if skipped:
            domains = [d['domain'] for d in skipped]
            parts.append(f"It's okay to skip {', '.join(domains)} today – rest is productive too.")
        
        parts.append("You're making a smart choice by listening to your body! 💪")
        
        return {
            "explanation": " ".join(parts),
            "temporal_analysis": "Urgency: Low. Recommendation: Consistent routine detected.",
            "context_assessment": "Risk Level: Low. Conditions favorable for planned activities."
        }
    
    def _format_decisions(self, decisions: list) -> str:
        """Format decisions for LLM prompt."""
        lines = []
        for d in decisions:
            action = d.get('action', 'MAINTAIN')
            domain = d.get('domain', 'unknown')
            reasoning = d.get('reasoning', '')
            lines.append(f"- {domain.upper()}: {action} - {reasoning}")
        return "\n".join(lines) if lines else "No specific decisions"
    
    def _format_impacts(self, impacts: list) -> str:
        """Format future impacts for LLM prompt."""
        lines = []
        for i in impacts:
            desc = i.get('description', '')
            lines.append(f"- {desc}")
        return "\n".join(lines) if lines else "No future adjustments"
    
    def generate_weekly_insight(
        self,
        adaptation_report: dict
    ) -> str:
        """Generate weekly insight based on adaptation patterns."""
        if not self.client:
            return self._template_weekly_insight(adaptation_report)
        
        try:
            domains = adaptation_report.get('domains', {})
            recommendations = adaptation_report.get('recommendations', [])
            
            prompt = f"""Based on this weekly health pattern data, provide an encouraging weekly insight:

**Domain Adherence:**
{chr(10).join(f"- {d}: {s.get('skip_rate', 0):.0f}% skipped, {s.get('downgrade_rate', 0):.0f}% downgraded" for d, s in domains.items())}

**System Recommendations:**
{chr(10).join(f"- {r}" for r in recommendations) if recommendations else "No specific recommendations"}

Provide a 2-3 sentence supportive weekly insight that acknowledges patterns and encourages improvement."""

            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return self._template_weekly_insight(adaptation_report)
    
    def _template_weekly_insight(self, report: dict) -> str:
        """Template-based weekly insight."""
        domains = report.get('domains', {})
        recommendations = report.get('recommendations', [])
        
        # Find best and worst adherence
        best = min(domains.items(), key=lambda x: x[1].get('skip_rate', 0), default=None)
        worst = max(domains.items(), key=lambda x: x[1].get('skip_rate', 0), default=None)
        
        parts = ["📊 **Weekly Insight:**"]
        
        if best:
            parts.append(f"Great job staying consistent with {best[0]}!")
        
        if worst and worst[1].get('skip_rate', 0) > 30:
            parts.append(f"Consider adjusting your {worst[0]} goals to be more achievable.")
        
        if recommendations:
            parts.append(recommendations[0])
        
        parts.append("Remember: consistency over perfection! 🌟")
        
        return " ".join(parts)


    def generate_daily_tasks(
        self,
        state_snapshot: dict,
        user_goal: str,
        user_profile: dict
    ) -> list[dict]:
        """Generate a list of recommended daily tasks based on state and goal."""
        
        # Fallback tasks if LLM fails or is unavailable
        fallback_tasks = [
            {"id": "1", "title": "Light Stretching", "duration": 15, "domain": "fitness", "reason": "Low energy detected, focus on mobility."},
            {"id": "2", "title": "Mindful Breathing", "duration": 10, "domain": "wellness", "reason": "Manage daily stress."}
        ]

        if not self.client:
            return fallback_tasks

        try:
            prompt = f"""As a High-Performance Strategist & Health Coach, generate 3-5 aggressive, goal-oriented daily tasks for a user with the following profile:

**User Profile:**
- Name: {user_profile.get('name', 'User')}
- Age: {user_profile.get('age', 30)}
- Goal: {user_goal}

**Current State:**
- Sleep: {state_snapshot.get('sleep_hours')}h
- Energy: {state_snapshot.get('energy_level')}/10
- Stress: {state_snapshot.get('stress_level')}
- Available Time: {state_snapshot.get('available_time')}h

CIRCUIT BREAKER PROTOCOLS (ABSOLUTE OVERRIDES - CHECK FIRST):
1. **CRITICAL SLEEP**: IF Sleep < 5 hours AND Goal implies High Intensity -> GENERATE the High Intensity task but MARK IT BLOCKED.
   - Set "is_blocked": true
   - Set "block_reason": "Circuit Breaker: Critical Sleep Debt. High intensity increases cortisol."
2. **BURNOUT RISK**: IF Stress is High -> MARK Cognitive/Focus tasks as BLOCKED.
   - Set "is_blocked": true
   - Set "block_reason": "Circuit Breaker: High Stress. Brain rest required."
3. **LOW ENERGY**: IF Energy < 4 -> MARK High Intensity tasks as BLOCKED.

Rules (Apply if not blocked):
1. REQUIRED DISTRIBUTION:
   - 1-2 Fitness tasks (Aggressive)
   - 1 Wellness task
   - 1 Nutrition task
   - 1 Mindfulness task
2. PRIORITIZE THE USER'S GOAL. Be aggressive.
3. If Energy is High (7+), push for maximum intensity/productivity in Fitness.
4. Provide a short, punchy 'reason' connecting the task to their goal.

Output valid JSON ONLY in this format:
[
  {{ "title": "Task Name", "duration": 30, "domain": "fitness", "reason": "Explanation", "is_blocked": false, "block_reason": null }}
]"""
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a high-performance coach. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            import json
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Handle potential wrapper keys like {"tasks": [...]}
            if isinstance(data, dict):
                if "tasks" in data:
                    return data["tasks"]
                # If meant to be a list but wrapped in a key
                for key in data:
                    if isinstance(data[key], list):
                        return data[key]
            
            if isinstance(data, list):
                return data
                
            return fallback_tasks

        except Exception as e:
            print(f"LLM Task Gen Error: {e}")
            return fallback_tasks



    def analyze_single_task(
        self,
        task_title: str,
        state_snapshot: dict
    ) -> dict:
        """
        Analyze a single task to determine domain and safety status based on state.
        """
        default_analysis = {
            "domain": "productivity",
            "is_safe": True,
            "reason": "Standard task."
        }
        
        if not self.client:
            return default_analysis
            
        try:
            prompt = f"""Analyze this task for a user with the following state:
            
**Task:** "{task_title}"

**Current State:**
- Sleep: {state_snapshot.get('sleep_hours')}h
- Energy: {state_snapshot.get('energy_level')}/10
- Stress: {state_snapshot.get('stress_level')}

Determine:
1. The most appropriate domain (Fitness, Nutrition, Mindfulness, Productivity, Wellness).
2. Is it safe/appropriate given the simplified state? (e.g. High intensity fitness is unsafe if Energy < 4 or Sleep < 5).
3. A short reasoning string (max 10 words).

Output valid JSON ONLY:
{{ "domain": "Fitness", "is_safe": false, "reason": "Energy too low for cardio." }}
"""
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a health analysis engine. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100,
                response_format={"type": "json_object"}
            )
            
            import json
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            print(f"LLM Task Analysis Error: {e}")
            return default_analysis


# Convenience function
def get_llm_generator() -> LLMReasoningGenerator:
    """Get an LLM generator, configured from environment."""
    return LLMReasoningGenerator.from_env()
