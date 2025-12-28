from dataclasses import dataclass
from typing import List, Optional
import re
import os

@dataclass
class NegotiationResult:
    status: str  # "ACCEPTED", "NEGOTIATE", "REJECTED"
    counter_proposal: Optional[str] = None
    reasoning: str = ""
    safety_score: float = 1.0  # 0.0 to 1.0

class GoalNegotiator:
    """
    Agent that acts as a gatekeeper for user goals, ensuring they are 
    biologically realistic and safe.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.role = "Goal Integrity Guardian"
        
        # Try Initialize Groq
        self.client = None
        key = api_key or os.getenv("GROQ_API_KEY")
        try:
            from groq import Groq
            if key:
                self.client = Groq(api_key=key)
        except ImportError:
            pass
            
    def evaluate_goal(self, goal_text: str, current_health_state: dict) -> NegotiationResult:
        """
        Evaluates a user goal against health constraints using LLM first, then heuristics.
        """
        # 1. Try LLM Evaluation (Agentic)
        if self.client:
            try:
                system_prompt = """You are an expert Medical Safety Agent. Evaluate User Goal.
Target: Detect UNSAFE, UNREALISTIC, or DANGEROUS health goals (e.g. extreme weight loss/gain, sleep deprivation).
Output STRICT JSON:
{
 "status": "ACCEPTED" | "NEGOTIATE" | "REJECTED",
 "counter_proposal": "Better alternative (or null if accepted)",
 "reasoning": "Medical/Scientific reason (max 1 sentence)",
 "safety_score": 0.0-1.0
}
Unsafe definitions:
- Weight loss > 1.2kg/week
- Weight gain > 0.8kg/week
- Sleep < 6h/night
- "No rest days"
"""
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Goal: {goal_text}"}
                    ],
                    response_format={"type": "json_object"}
                )
                import json
                data = json.loads(response.choices[0].message.content)
                return NegotiationResult(
                    status=data["status"],
                    counter_proposal=data.get("counter_proposal"),
                    reasoning=data["reasoning"],
                    safety_score=float(data["safety_score"])
                )
            except Exception as e:
                print(f"LLM Error: {e} - Falling back to regex")
                pass # Fallback to regex
        
        # 2. HEURISTIC FALLBACK (Regex)
        goal_lower = goal_text.lower()
        
        # ... (Existing Regex Logic) ...
        # Check for unsafe weight change velocity (Loss OR Gain)
        # Heuristic: > 1kg/week is flagged
        weight_match = re.search(r"(lose|gain) (\d+)\s*(kg|lbs)", goal_lower)
        time_match = re.search(r"in (\d+)\s*(day|week|month)", goal_lower)
        
        if weight_match and time_match:
            direction = weight_match.group(1) # "lose" or "gain"
            amount = int(weight_match.group(2))
            unit = weight_match.group(3)
            duration = int(time_match.group(1))
            period = time_match.group(2)
            
            # Normalize to kg/week
            kg_amount = amount if unit == "kg" else amount * 0.45
            weeks_duration = duration if period == "week" else (duration / 7 if period == "day" else duration * 4)
            
            rate = kg_amount / weeks_duration if weeks_duration > 0 else 999
            
            # Safety Thresholds
            # Loss: > 1.0 kg/week is aggressive
            # Gain: > 0.5 kg/week is mostly fat/unsafe for heart
            limit = 1.0 if direction == "lose" else 0.5
            
            if rate > limit:
                recommended_weeks = int(kg_amount / (limit * 0.8)) # Aim slightly below limit
                msg_dir = "losing" if direction == "lose" else "gaining"
                return NegotiationResult(
                    status="NEGOTIATE",
                    counter_proposal=f"{direction.title()} {amount}{unit} in {recommended_weeks} weeks",
                    reasoning=f"Your goal implies {msg_dir} {rate:.1f}kg/week. Medically safe limit is ~{limit}kg/week to avoid health risks.",
                    safety_score=0.4
                )

        # Check for sleep deprivation goals
        if "sleep less" in goal_lower or "4 hours" in goal_lower:
             return NegotiationResult(
                status="REJECTED",
                counter_proposal="Optimize Deep Sleep Quality (8h total)",
                reasoning="Reducing sleep duration below baseline is cognitively hazardous. I cannot support a goal that actively damages your neurobiology.",
                safety_score=0.1
            )

        # Check for "No Rest" mentality
        if "every day" in goal_lower and ("run" in goal_lower or "gym" in goal_lower or "train" in goal_lower):
            return NegotiationResult(
                status="NEGOTIATE",
                counter_proposal=goal_text.replace("every day", "5 days/week"),
                reasoning="Training every day leads to overtraining syndrome. Professional athletes take rest days. I propose 5 days/week to maximize adaptation.",
                safety_score=0.6
            )
            
        # Default: Accept
        return NegotiationResult(
            status="ACCEPTED",
            reasoning="This goal appears ambitious yet sustainable given your current profile.",
            safety_score=0.95
        )
