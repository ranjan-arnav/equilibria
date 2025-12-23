# Equilibra - AI Health Balance System

**Professional Multi-Agent System for Burnout Prevention and Wellness Optimization**

Built for the Innov-AI-tion Healthcare & Fitness Hackathon

---

## Overview

Equilibra is an advanced agentic AI system that prevents burnout through multi-agent collaboration and temporal reasoning. Unlike traditional health trackers that simply log data, Equilibra actively deliberates, predicts crises, and intervenes before problems occur.

### Key Features

- **Multi-Agent Health Council**: 4 specialized AI agents (Sleep Specialist, Performance Coach, Wellness Guardian, Future Self) collaborate to make decisions
- **Temporal Reasoning Engine**: Analyzes past patterns, present context, and future trajectories to provide proactive guidance
- **Predictive Crisis Mode**: Forecasts burnout 3-7 days in advance and automatically activates protective measures
- **Voice Interaction**: Speak to the AI using voice input powered by Groq Whisper
- **Gamification**: Daily streak tracking and achievement system
- **Transparent AI**: See exactly how agents vote and why they reach consensus

---

## Problem Statement

Modern professionals face chronic stress and burnout due to competing demands across work, fitness, sleep, and personal life. Traditional health apps are reactive - they track what happened but don't prevent problems. Equilibra is proactive - it predicts crises and intervenes autonomously.

### Target Users

- Professionals managing multiple health domains
- Individuals at risk of burnout
- Anyone seeking data-driven wellness optimization

---

## System Architecture

```
User Input
    |
    v
Health Council (Multi-Agent Deliberation)
    |-- Sleep Specialist Agent
    |-- Performance Coach Agent
    |-- Wellness Guardian Agent
    |-- Future Self Agent
    |
    v
Consensus Mechanism
    |
    v
Temporal Reasoner
    |-- Past: Pattern Detection
    |-- Present: Risk Assessment
    |-- Future: Outcome Projection
    |
    v
Decision Engine + Crisis Detection
    |
    v
User Dashboard (Transparent UI)
```

---

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git
- Groq API key (free tier available at https://console.groq.com)

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/equilibra.git
cd equilibra
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

To get a free Groq API key:
1. Visit https://console.groq.com
2. Sign up for a free account
3. Generate an API key
4. Copy it to your `.env` file

### Step 4: Run the Application

```bash
python -m streamlit run ui/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

---

## Usage Guide

### First Time Setup

1. **Onboarding**: Complete the 4-step personalized onboarding
   - Enter your name
   - Set your age
   - Choose your primary health goal
   - Review your personalized welcome

2. **Explore the Dashboard**: Navigate through the tabs
   - **Home**: View your daily metrics and burnout risk
   - **Council**: See multi-agent deliberation in action
   - **Make Decision**: Run the decision engine
   - **Chat**: Talk to the AI (text or voice)
   - **History**: Review past decisions

### Making Your First Decision

1. Go to the **Make Decision** tab
2. Adjust your current state in the sidebar:
   - Sleep hours
   - Energy level (1-10)
   - Stress level (Low/Moderate/High)
3. Click "Run Agent Decision"
4. Review the recommendations

### Using the Health Council

1. Make at least one decision first
2. Go to the **Council** tab
3. See how 4 agents voted:
   - Each agent's recommendation (PROCEED/MODIFY/SKIP)
   - Confidence scores
   - Individual reasoning
   - Final consensus
4. Review temporal insights:
   - Detected patterns from your history
   - Current risk assessment
   - Future projections with intervention windows

### Voice Interaction

1. Go to the **Chat** tab
2. Click the microphone icon
3. Speak your question
4. The AI will transcribe and respond

---

## Project Structure

```
equilibra/
|-- src/
|   |-- agents/
|   |   |-- chat_agent.py          # Conversational AI
|   |   |-- burnout_predictor.py   # Crisis forecasting
|   |   |-- health_council.py      # Multi-agent system
|   |   |-- temporal_reasoner.py   # Temporal analysis
|   |-- core/
|   |   |-- config.py               # Configuration
|   |-- models/
|   |   |-- decision.py             # Data models
|   |   |-- user.py                 # User profiles
|   |-- utils/
|   |   |-- audio_transcriber.py    # Voice input
|-- ui/
|   |-- streamlit_app.py            # Main UI
|-- requirements.txt                # Dependencies
|-- .env                            # API keys (create this)
|-- README.md                       # This file
```

---

## Agentic Capabilities

### 1. Multi-Agent Collaboration

Four specialized agents with distinct priorities:

- **Sleep Specialist**: Prioritizes recovery (weights: Sleep 1.5x, Exercise 0.7x)
- **Performance Coach**: Maximizes productivity (weights: Work 1.4x, Exercise 1.3x)
- **Wellness Guardian**: Balances mental health (weights: Mindfulness 1.5x, Work 0.7x)
- **Future Self**: Advocates for long-term habits (analyzes skip patterns)

Agents vote independently, then reach consensus through weighted majority.

### 2. Temporal Reasoning

**Past Analysis**:
- Detects day-of-week patterns (e.g., "Monday workout avoidance")
- Identifies stress-triggered behaviors
- Tracks sleep debt cascades

**Present Assessment**:
- Contextualizes current moment (day, time, similar past situations)
- Calculates real-time risk score
- Identifies active risk factors

**Future Projection**:
- Predicts outcomes across multiple timelines (24h, 1 week, 1 month)
- Estimates probability and impact
- Provides intervention windows

### 3. Autonomous Decision-Making

- **Goal-Oriented**: Aligns decisions with user's stated goals
- **Constraint-Aware**: Respects biological limits (sleep, stress, energy)
- **Adaptive**: Learns from user feedback and patterns
- **Proactive**: Intervenes before crises occur

---

## Technical Stack

### Core Frameworks
- **Streamlit**: Web UI framework
- **LangChain**: LLM orchestration
- **Groq**: Fast LLM inference (llama-3.3-70b-versatile)

### AI/ML
- **Multi-Agent System**: Custom implementation with consensus mechanism
- **Temporal Reasoning**: Pattern detection and trajectory projection
- **Burnout Prediction**: Risk scoring algorithm

### Data & Visualization
- **Plotly**: Interactive charts
- **Pandas**: Data manipulation
- **Pydantic**: Data validation

---

## Limitations & Future Work

### Current Limitations

- **Non-Diagnostic**: Does not provide medical diagnosis or treatment
- **Synthetic Data**: Uses simulated wearable data (real integration planned)
- **English Only**: Currently supports English language only
- **Free Tier API**: Limited to Groq free tier rate limits

### Planned Enhancements

- Real wearable device integration (Oura, Whoop, Apple Health)
- Proactive intervention system with notifications
- Explainable AI dashboard with decision trees
- Dynamic goal negotiation
- Multi-language support

---

## Evaluation Criteria Alignment

This project was designed to excel across all hackathon evaluation dimensions:

**Novelty & Creativity (30%)**
- Multi-agent collaboration (unique in health domain)
- Temporal reasoning across three time dimensions
- Transparent deliberation process

**Agentic System Design (25%)**
- Autonomous decision-making with agent voting
- Multi-step planning via temporal projections
- Goal-oriented behavior and adaptation

**Implementation Quality (20%)**
- Clean separation of concerns
- Robust error handling
- Reproducible setup with clear documentation

**Scope & Usefulness (15%)**
- Addresses real burnout prevention problem
- Practical constraints (API limits, ethical boundaries)
- Immediate real-world applicability

**Documentation & Presentation (10%)**
- Comprehensive README
- Transparent AI reasoning
- Clear architecture diagrams

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

Built for the Innov-AI-tion Healthcare & Fitness Hackathon

**Technologies Used**:
- Groq (LLM inference)
- Streamlit (UI framework)
- LangChain (agent orchestration)
- Python 3.13

---

## Contact

For questions or feedback, please open an issue on GitHub.

**Demo Video**: [Link to be added]

**Live Demo**: Run locally following setup instructions above
