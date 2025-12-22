# HTPA - Agentic Behaviors Documentation

## What Makes This Agentic?

This document explains the autonomous, agentic behaviors implemented in HTPA.

---

## 1. Autonomous Decision-Making

The agent makes decisions **without waiting for user commands**:

```python
# User provides: wearable data + available time
# Agent autonomously: analyzes → evaluates → decides → adjusts

decision = orchestrator.run_daily_decision(
    wearable_data=wearable,
    time_available_hours=1.5,
    planned_tasks=tasks
)
# Agent returns: complete prioritization with reasoning
```

**Key Behavior**: User never says "skip my workout" - the agent decides this based on signals.

---

## 2. Multi-Step Reasoning Pipeline

The agent performs a 5-step reasoning chain:

```
Step 1: STATE ANALYSIS
├── Ingest wearable data (sleep, HRV, steps)
├── Derive stress level from HRV + HR
├── Calculate energy from sleep quality
└── Build HealthState snapshot

Step 2: CONSTRAINT EVALUATION  
├── Check sleep thresholds (< 6h = low, < 5h = critical)
├── Check energy levels (< 4 = low, < 2 = critical)
├── Detect compound burnout signals
└── Output: ActiveConstraints with severity scores

Step 3: PRIORITY ADJUSTMENT
├── Start with base priorities (recovery: 0.30, nutrition: 0.25...)
├── Apply constraint modifiers (+0.25 recovery if critical_sleep)
├── Normalize to sum = 1.0
└── Output: Adjusted priority matrix

Step 4: TRADE-OFF DECISIONS
├── Rank domains by adjusted priority
├── Allocate available capacity top-down
├── Generate PRIORITIZE/MAINTAIN/DOWNGRADE/SKIP per domain
└── Output: TradeOffDecision with reasoning

Step 5: FUTURE ADAPTATION
├── Calculate future impacts (intensity reduction, rest days)
├── Detect patterns from history
├── Modify upcoming plan
└── Output: Adapted future schedule
```

---

## 3. Constraint-Based Prioritization

The agent explicitly handles 10+ constraint types:

| Constraint | Trigger | Effect |
|------------|---------|--------|
| `critical_sleep` | < 5 hours | +0.25 recovery, -0.20 fitness |
| `high_stress` | HRV low + HR high | +0.20 mindfulness, -0.10 fitness |
| `burnout_warning` | 3+ risk factors | Skip fitness, deload week |
| `time_critical` | < 30 min available | Only essential tasks |
| `overtraining_risk` | 3+ high-effort days | Force active recovery |

---

## 4. Transparent Reasoning

Every decision includes explicit justification:

```json
{
  "domain": "fitness",
  "action": "DOWNGRADE",
  "original": "HIIT Workout (45min)",
  "adjusted": "Light stretching (10min)",
  "reasoning": "Critical fatigue - replacing HIIT to maintain movement habit without adding stress",
  "priority_score": 0.15
}
```

---

## 5. Adaptation Over Time

The agent learns from patterns:

```python
# Pattern Detection
if skip_frequency("fitness") > 0.5:  # Skipped 50%+ of time
    → Reduce fitness expectations by 30%
    → Reasoning: "Current targets may be unrealistic"

if constraint_count("high_stress") >= 4:  # 4+ days/week
    → Increase mindfulness allocation
    → Reasoning: "Persistent stress pattern detected"
```

---

## 6. LLM-Enhanced Explanations

Natural language coaching powered by Groq:

> "I can see you're running on low reserves today. I've prioritized recovery and mindfulness to give you what you need most. It's okay to skip the workout today – rest is productive too. You're making a smart choice by listening to your body! 💪"

---

## Demo Scenarios

| Scenario | Constraints | Agent Behavior |
|----------|-------------|----------------|
| Burnout Day | 4h sleep, high stress | Skip fitness → deload 3 days |
| Time Crunch | Only 30 min available | Minimal versions of top priorities |
| High Stress | Work deadline | Prioritize mindfulness + recovery |
| Well Rested | 8h sleep, low stress | Maintain all tasks as planned |

---

## Why This Matters for Hackathon

✅ **Autonomous**: Makes decisions without explicit commands  
✅ **Multi-step**: 5-stage reasoning pipeline  
✅ **Constraint-aware**: Explicit trade-off handling  
✅ **Transparent**: Full reasoning logs  
✅ **Adaptive**: Pattern-based learning  
✅ **NOT a chatbot**: Decision engine, not Q&A
