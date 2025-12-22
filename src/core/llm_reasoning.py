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
    ) -> str:
        """
        Generate a natural language explanation for a decision.
        
        Falls back to template-based explanation if LLM unavailable.
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
    ) -> str:
        """Generate explanation using Groq LLM."""
        user_prompt = f"""Based on this health data and decision, provide a supportive explanation:

**Today's State:**
- Sleep: {state_snapshot.get('sleep_hours', 'N/A')} hours
- Energy: {state_snapshot.get('energy_level', 'N/A')}/10
- Stress: {state_snapshot.get('stress_level', 'N/A')}
- Available time: {state_snapshot.get('time_available_hours', 'N/A')} hours

**Active Constraints:** {', '.join(constraints) if constraints else 'None'}

**Decisions Made:**
{self._format_decisions(decision_summary.get('decisions', []))}

**Future Adjustments:**
{self._format_impacts(decision_summary.get('future_impacts', []))}

Provide a warm, supportive 3-4 sentence explanation of these decisions."""

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        return response.choices[0].message.content
    
    def _template_explanation(
        self,
        decision_summary: dict,
        state_snapshot: dict,
        constraints: list[str]
    ) -> str:
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
        downgraded = [d for d in decisions if d.get('action') == 'DOWNGRADE']
        
        if prioritized:
            domains = [d['domain'] for d in prioritized]
            parts.append(f"I've prioritized {', '.join(domains)} to give you the biggest benefit.")
        
        if skipped:
            domains = [d['domain'] for d in skipped]
            parts.append(f"It's okay to skip {', '.join(domains)} today – rest is productive too.")
        
        if downgraded:
            parts.append("I've adjusted some activities to lighter versions that still count.")
        
        # Future encouragement
        impacts = decision_summary.get('future_impacts', [])
        if impacts:
            parts.append("I've also adjusted your plan for the next few days to help you recover.")
        
        parts.append("You're making a smart choice by listening to your body! 💪")
        
        return " ".join(parts)
    
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


# Convenience function
def get_llm_generator() -> LLMReasoningGenerator:
    """Get an LLM generator, configured from environment."""
    return LLMReasoningGenerator.from_env()
