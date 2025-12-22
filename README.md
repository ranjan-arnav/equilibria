# Autonomous Health Trade-Off & Prioritization Agent (HTPA)

An agentic system that autonomously prioritizes health behaviors under real-world constraints.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional for Groq)
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# Run the demo
streamlit run ui/streamlit_app.py

# Run tests
pytest tests/ -v
```

## Architecture

The system uses 4 specialized agents:

1. **State Analyzer** - Ingests wearable data and builds health snapshots
2. **Constraint Evaluator** - Identifies active constraints (time, energy, stress)
3. **Trade-Off Engine** - Makes prioritization decisions with explicit reasoning
4. **Plan Adjuster** - Rebalances future plans based on decisions

## Key Features

- **Autonomous Trade-Off Decisions**: Prioritizes what to do, skip, or downgrade
- **Transparent Reasoning**: Every decision includes explicit justification
- **Adaptive Planning**: Learns from patterns to prevent burnout
- **Constraint-Aware**: Handles time, energy, stress, and recovery limits

## Project Structure

```
src/
├── agents/           # Agent implementations
├── models/           # Data models
├── core/             # Priority matrix, reasoning logger
├── data/             # Data generators and loaders
└── main.py           # Orchestration
ui/                   # Streamlit interface
data/                 # Sample data files
logs/                 # Decision logs
tests/                # Unit tests
```

## License

MIT - Built for HYD-300 Hackathon
