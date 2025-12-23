"""
Conversational Agent - Natural language interface for the HTPA system.
"""
import os
from typing import Optional
from datetime import datetime

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

from src.models import TradeOffDecision, HealthState
from src.utils.audio_transcriber import AudioTranscriber


class ConversationalAgent:
    """
    Natural language interface for interacting with the HTPA system.
    Allows users to ask questions about decisions, get advice, etc.
    """
    
    SYSTEM_PROMPT = """You are HTPA (Health Trade-off Prioritization Agent), a supportive, empathetic AI health coach.

Your personality:
- Warm and encouraging, never judgmental
- Explains decisions in simple, friendly language
- Focuses on sustainability and long-term health
- Celebrates small wins and reframes setbacks positively

You have access to the user's current health state and recent decisions. Use this context to provide personalized responses.

Guidelines:
- Keep responses concise (2-4 sentences unless asked for detail)
- Use emojis sparingly but warmly 💪
- Never give medical advice - you're a wellness coach, not a doctor
- When explaining trade-offs, emphasize the positive reasoning

Current Context:
{context}"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        self.model = "llama-3.3-70b-versatile"
        
        if self.api_key and GROQ_AVAILABLE:
            self.client = Groq(api_key=self.api_key)
        
        # Conversation history
        self.messages: list[dict] = []
        
        # Context from HTPA system
        self.current_state: Optional[HealthState] = None
        self.last_decision: Optional[TradeOffDecision] = None
        self.decision_history: list[TradeOffDecision] = []
        self.user_profile: dict = {}
        
        # Audio
        self.transcriber = AudioTranscriber(self.api_key)
    
    def update_context(
        self,
        state: Optional[HealthState] = None,
        decision: Optional[TradeOffDecision] = None,
        history: Optional[list[TradeOffDecision]] = None,
        user_profile: Optional[dict] = None
    ):
        """Update the agent's context with latest data."""
        if state:
            self.current_state = state
        if decision:
            self.last_decision = decision
        if history:
            self.decision_history = history
        if user_profile:
            self.user_profile = user_profile
    

    def _build_context(self) -> str:
        """Build context string for the LLM."""
        parts = []
        
        if self.user_profile:
            parts.append(f"""User Profile:
- Name: {self.user_profile.get('name', 'User')}
- Age: {self.user_profile.get('age', 'N/A')}
- Primary Goal: {self.user_profile.get('goal', 'N/A')}
- Current Adherence: {self.user_profile.get('adherence', 'N/A')}%""")
        
        if self.current_state:
            parts.append(f"""Current State:
- Sleep: {self.current_state.sleep_hours}h (quality: {self.current_state.sleep_quality:.0f}/100)
- Energy: {self.current_state.energy_level}/10
- Stress: {self.current_state.stress_level.value}
- Time available: {self.current_state.time_available_hours}h""")
        
        if self.last_decision:
            parts.append(f"""
Last Decision (ID: {self.last_decision.decision_id}):
- Constraints: {', '.join(self.last_decision.constraints_active) or 'None'}
- Actions taken: {', '.join(f"{d.domain.value}: {d.action.value}" for d in self.last_decision.decisions)}
- Reasoning: {self.last_decision.reasoning_summary}""")
        
        if self.decision_history and len(self.decision_history) > 1:
            parts.append(f"""
Recent History:
- Decisions made: {len(self.decision_history)}
- Most common constraints: Check history for patterns""")
        
        return "\n".join(parts) if parts else "No current context available."
    
    def chat(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.
        """
        # Add user message to history
        self.messages.append({"role": "user", "content": user_message})
        
        # Use LLM if available
        if self.client:
            try:
                return self._llm_response(user_message)
            except Exception as e:
                print(f"LLM error: {e}")
                return self._template_response(user_message)
        else:
            return self._template_response(user_message)

    def transcribe_audio(self, audio_file) -> Optional[str]:
        """Transcribe audio input to text."""
        return self.transcriber.transcribe(audio_file)
    
    def _llm_response(self, user_message: str) -> str:
        """Generate response using Groq LLM."""
        context = self._build_context()
        system_prompt = self.SYSTEM_PROMPT.format(context=context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            *self.messages[-10:]  # Keep last 10 messages for context
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        assistant_message = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    def _template_response(self, user_message: str) -> str:
        """Generate template-based response when LLM unavailable."""
        user_lower = user_message.lower()
        
        # Intent detection
        if any(w in user_lower for w in ["why", "skip", "didn't", "not"]):
            return self._explain_skip()
        elif any(w in user_lower for w in ["focus", "should", "recommend", "suggest"]):
            return self._give_recommendation()
        elif any(w in user_lower for w in ["how", "doing", "week", "progress"]):
            return self._weekly_summary()
        elif any(w in user_lower for w in ["tired", "exhausted", "burnout", "stressed"]):
            return self._acknowledge_fatigue()
        elif any(w in user_lower for w in ["hi", "hello", "hey"]):
            return "Hey there! 👋 I'm HTPA, your health trade-off coach. I'm here to help you make smart choices about your health activities. What would you like to know?"
        else:
            return self._general_response()
    
    def _explain_skip(self) -> str:
        if self.last_decision:
            skipped = [d for d in self.last_decision.decisions if d.action.value == "SKIP"]
            if skipped:
                domain = skipped[0].domain.value
                reason = skipped[0].reasoning
                return f"I suggested skipping {domain} because {reason}. It's not about giving up - it's about being smart! Rest now, perform better tomorrow. 💪"
        return "Sometimes skipping is the smartest choice! When your body signals fatigue, pushing through can lead to burnout. Recovery is productive too."
    
    def _give_recommendation(self) -> str:
        if self.current_state:
            if self.current_state.stress_level.value == "high":
                return "With your stress levels elevated, I'd focus on mindfulness and recovery today. Even 10 minutes of breathing exercises can help reset your system. 🧘"
            elif self.current_state.energy_level < 4:
                return "Your energy is pretty low right now. Light movement like a walk is great, but skip intense workouts. Focus on sleep and nutrition to rebuild your reserves."
            else:
                return "You're in a good spot today! This is a great day for your planned activities. Don't forget to celebrate the good days too! 🌟"
        return "Based on how you're feeling, focus on what gives you energy today. If something feels like a chore, it's okay to do a lighter version."
    
    def _weekly_summary(self) -> str:
        if self.decision_history and len(self.decision_history) >= 3:
            total = len(self.decision_history)
            return f"You've made {total} decisions this week. I've been adapting your plan to match your energy levels. Consistency matters more than perfection - keep listening to your body!"
        return "We're just getting started tracking your patterns! After a few more days, I'll have better insights about your weekly trends."
    
    def _acknowledge_fatigue(self) -> str:
        return "I hear you - fatigue is tough. 😔 The good news? Recognizing it is step one. Today, let's focus on recovery. Skip the intense stuff, prioritize rest, and know that tomorrow can be better. You're doing great by listening to your body."
    
    def _general_response(self) -> str:
        responses = [
            "I'm here to help you make smart health trade-offs. Ask me about why I made a decision, what to focus on, or how your week is going!",
            "Think of me as your health decision assistant. I look at your signals - sleep, stress, energy - and help prioritize what matters most today.",
            "Every day is different! That's why I adapt your plan based on how you're actually doing, not just what was scheduled."
        ]
        import random
        return random.choice(responses)
    
    def clear_history(self):
        """Clear conversation history."""
        self.messages = []


# Quick access function
def get_chat_agent() -> ConversationalAgent:
    """Get a configured chat agent."""
    return ConversationalAgent()
