"""
Equilibra - Professional AI Health Balance System
Streamlit UI for the Health Trade-Off & Prioritization Agent
"""
import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import random

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import HTPAOrchestrator, create_sample_planned_tasks
from src.models import (
    UserProfile, HealthState, WearableData, StressLevel, EnergyLevel,
    TradeOffDecision, PlannedTask, HealthDomain, DecisionAction,
    FitnessGoal, ActivityLevel, DomainPreferences
)
from src.models.predictive_engine import (
    ReadinessForecaster, 
    WorkloadRecommender, 
    BurnoutClassifier, 
    BurnoutRisk
)
from src.models.future_agent import FutureSelfAgent
from src.agents import ConversationalAgent, get_chat_agent
from src.data import SyntheticDataGenerator

# Page config with custom menu items in Streamlit's toolbar
st.set_page_config(
    page_title="Equilibra - AI Health Balance",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': '''
        ## ⚙️ Equilibra Settings
        
        **Dark Mode**: Use the toggle in the Settings panel below the header.
        
        **API Configuration**: Add your Groq API key in Settings for enhanced AI explanations.
        
        ---
        
        **Equilibra v2.0.0**  
        Professional AI Health Balance System
        
        Built for HYD-300 Hackathon
        '''
    }
)

# Initialize session state
def init_session_state():
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    if "last_decision" not in st.session_state:
        st.session_state.last_decision = None
    if "chat_agent" not in st.session_state:
        st.session_state.chat_agent = get_chat_agent()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "wearable_data" not in st.session_state:
        st.session_state.wearable_data = None
    if "decision_history" not in st.session_state:
        st.session_state.decision_history = []
    if "adherence_score" not in st.session_state:
        st.session_state.adherence_score = 85
    if "simulation_results" not in st.session_state:
        st.session_state.simulation_results = None


init_session_state()


def get_theme_css():
    """Generate CSS for the app styling with premium dark mode enforced."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * { font-family: 'Inter', sans-serif; }
        
        /* Main app - premium dark gradient */
        .stApp {
            background: linear-gradient(135deg, #0d0d0d 0%, #1a1a2e 40%, #16213e 70%, #0f3460 100%);
        }
        
        .main .block-container {
            padding-top: 1rem;
            max-width: 1200px;
        }
        
        /* All text to light color */
        h1, h2, h3, h4, h5, h6, p, span, div, label, li {
            color: #e8e8e8 !important;
        }
        
        /* Sidebar - dark maroon with gradient */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #4a3728 0%, #3d2e23 100%);
            border-right: 1px solid rgba(255, 152, 100, 0.15);
        }
        
        [data-testid="stSidebar"] * {
            color: #e0e0e0 !important;
        }
        
        [data-testid="stSidebar"] .stSelectbox > div > div {
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 8px !important;
            color: white !important;
        }
        
        [data-testid="stSidebar"] .stSelectbox svg {
            fill: #f97316 !important;
        }
        
        [data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] {
            color: #f97316 !important;
            font-weight: 600;
        }
        
        /* Slider track color - orange glow */
        [data-testid="stSidebar"] .stSlider > div > div > div > div {
            background: linear-gradient(90deg, #f97316 0%, #fb923c 100%) !important;
            box-shadow: 0 0 10px rgba(249, 115, 22, 0.4);
        }
        
        /* Checkbox styling in sidebar */
        [data-testid="stSidebar"] .stCheckbox label span {
            color: #e0e0e0 !important;
        }
        
        /* State display */
        .state-label {
            color: #888 !important;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
            opacity: 0.7;
        }
        
        .state-value {
            font-size: 2rem;
            font-weight: 700;
            color: #ffffff !important;
            text-shadow: 0 0 20px rgba(255,255,255,0.1);
        }
        
        /* Info box styling - glassmorphism */
        .info-box {
            background: rgba(251, 191, 36, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(251, 191, 36, 0.3);
            border-radius: 12px;
            padding: 14px 18px;
            margin: 15px 0;
            display: flex;
            align-items: center;
            gap: 12px;
            color: #fcd34d !important;
        }
        
        .info-box.blue {
            background: rgba(59, 130, 246, 0.1);
            border-color: rgba(59, 130, 246, 0.3);
            color: #93c5fd !important;
        }
        
        /* Decision cards - glassmorphism */
        .decision-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 22px;
            margin: 12px 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        .decision-card:hover {
            background: rgba(255, 255, 255, 0.05);
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        }
        
        .decision-card.prioritize { 
            border-left: 4px solid #10b981;
            box-shadow: 0 8px 32px rgba(16, 185, 129, 0.15);
        }
        .decision-card.maintain { 
            border-left: 4px solid #3b82f6;
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.15);
        }
        .decision-card.downgrade { 
            border-left: 4px solid #f59e0b;
            box-shadow: 0 8px 32px rgba(245, 158, 11, 0.15);
        }
        .decision-card.skip { 
            border-left: 4px solid #ef4444;
            box-shadow: 0 8px 32px rgba(239, 68, 68, 0.15);
        }
        
        /* Tab styling - modern dark */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            padding: 4px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border: none;
            padding: 10px 18px;
            font-weight: 500;
            color: #888 !important;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(255, 255, 255, 0.05);
            color: #fff !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4);
        }
        
        /* Metric styling */
        [data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-weight: 700;
        }
        
        [data-testid="stMetricLabel"] {
            color: #888 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.75rem !important;
        }
        
        [data-testid="stMetricDelta"] {
            color: #10b981 !important;
        }
        
        /* Architecture box */
        .architecture-box {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 18px;
            font-family: 'Fira Code', 'Courier New', monospace;
            font-size: 0.85rem;
            color: #a0a0a0 !important;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4) !important;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: rgba(255, 255, 255, 0.03) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
        
        /* Chat message styling */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px !important;
        }
        
        /* Input styling */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            color: #e0e0e0 !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #f97316 !important;
            box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.2) !important;
        }
        
        /* Radio buttons */
        .stRadio > div {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            padding: 8px;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.02);
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        /* Spinner/loading */
        .stSpinner > div {
            border-color: #f97316 transparent transparent transparent !important;
        }
        
        footer {visibility: hidden;}
    </style>
    """


# Apply theme CSS
st.markdown(get_theme_css(), unsafe_allow_html=True)


# Sidebar - Today's Signals
def render_sidebar():
    with st.sidebar:
        st.markdown("### 📊 Today's Signals")
        
        # Load Scenario dropdown
        st.markdown("**Load Scenario**")
        scenario = st.selectbox(
            "Load Scenario",
            ["Custom", "Well Rested", "Sleep Deprived", "High Stress", "Time Crunch", "Recovery Day"],
            label_visibility="collapsed"
        )
        
        # Apply scenario presets
        if scenario == "Well Rested":
            default_sleep, default_energy, default_stress, default_time = 8.0, 8, "low", 3.0
        elif scenario == "Sleep Deprived":
            default_sleep, default_energy, default_stress, default_time = 4.5, 3, "high", 2.0
        elif scenario == "High Stress":
            default_sleep, default_energy, default_stress, default_time = 6.0, 5, "high", 1.5
        elif scenario == "Time Crunch":
            default_sleep, default_energy, default_stress, default_time = 7.0, 6, "medium", 0.5
        elif scenario == "Recovery Day":
            default_sleep, default_energy, default_stress, default_time = 9.0, 7, "low", 4.0
        else:
            default_sleep, default_energy, default_stress, default_time = 7.0, 6, "medium", 2.0
        
        st.markdown("---")
        
        # Sleep slider
        st.markdown("🌙 **Sleep (hours)**")
        sleep_hours = st.slider(
            "Sleep", 3.0, 10.0, default_sleep, 0.5,
            label_visibility="collapsed",
            key="sleep_slider"
        )
        
        # Energy slider
        st.markdown("⚡ **Energy Level**")
        energy_level = st.slider(
            "Energy", 1, 10, default_energy,
            label_visibility="collapsed",
            key="energy_slider"
        )
        
        # Stress level radio
        st.markdown("😰 **Stress Level**")
        stress_level = st.radio(
            "Stress",
            ["Low", "Medium", "High"],
            index=["low", "medium", "high"].index(default_stress),
            horizontal=True,
            label_visibility="collapsed",
            key="stress_radio"
        )
        
        # Available time slider
        st.markdown("⏰ **Available Time (hours)**")
        time_available = st.slider(
            "Time", 0.5, 4.0, default_time, 0.5,
            label_visibility="collapsed",
            key="time_slider"
        )
        
        st.markdown("---")
        
        # Planned Tasks
        st.markdown("### 📋 Planned Tasks")
        
        task1 = st.checkbox("🏋️ HIIT Workout (45min)", value=True, key="task_hiit")
        task2 = st.checkbox("🥗 Meal Prep (60min)", value=True, key="task_meal")
        task3 = st.checkbox("😴 Sleep Routine (30min)", value=True, key="task_sleep")
        task4 = st.checkbox("🧘 Meditation (20min)", value=True, key="task_meditation")
        
        return {
            "sleep_hours": sleep_hours,
            "energy_level": energy_level,
            "stress_level": stress_level.lower(),
            "time_available": time_available,
            "tasks": {
                "hiit": task1,
                "meal": task2,
                "sleep": task3,
                "meditation": task4
            }
        }


def render_header():
    """Render the main header with logo and adherence score."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div class="logo-section">
            <h1 style="margin: 0; font-size: 2rem;">💎 Equilibra</h1>
            <p style="margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.7;">Professional AI Health Balance System</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        score = st.session_state.adherence_score
        change = "+2%" if score >= 80 else "-1%"
        change_color = "#10b981" if "+" in change else "#ef4444"
        
        st.markdown(f"""
        <div style="text-align: right;">
            <div style="font-size: 0.75rem; opacity: 0.7;">Adherence Score</div>
            <div style="font-size: 2rem; font-weight: 600;">{score}%</div>
            <div style="font-size: 0.8rem; color: {change_color};">↑ {change}</div>
        </div>
        """, unsafe_allow_html=True)


def render_make_decision(inputs):
    """Render the Make Decision tab."""
    
    # --- NEW: AI PROJECTIONS SECTION ---
    from src.models.predictive_engine import ReadinessForecaster, WorkloadRecommender, BurnoutClassifier, BurnoutRisk
    from src.models.health_state import HealthState, StressLevel, EnergyLevel
    from src.models.bio_adaptive_engine import BioAdaptiveEngine, UIMode
    
    # Construct transient state for prediction based on current sliders
    from datetime import datetime
    
    stress_map = {
        "low": StressLevel.LOW, 
        "medium": StressLevel.MEDIUM, 
        "high": StressLevel.HIGH
    }
    
    # Estimate sleep debt based on input
    estimated_debt = max(0, 8.0 - inputs['sleep_hours'])
    if inputs['sleep_hours'] < 6:
        estimated_debt += 2 # Penalty for very low sleep
        
    temp_state = HealthState(
        timestamp=datetime.now(),
        sleep_hours=inputs['sleep_hours'],
        sleep_quality=85.0 if inputs['sleep_hours'] > 7 else 60.0,
        energy_level=int(inputs['energy_level']),
        stress_level=stress_map.get(inputs['stress_level'].lower(), StressLevel.MEDIUM),
        time_available_hours=inputs['time_available'],
        sleep_debt_hours=estimated_debt,
        consecutive_high_effort_days=2 # Assume average context
    )
    
    # --- CHAMELEON ENGINE ACTIVATION ---
    current_mode = BioAdaptiveEngine.determine_mode(temp_state)
    theme_css = BioAdaptiveEngine.get_theme_css(current_mode)
    st.markdown(theme_css, unsafe_allow_html=True)
    
    # Display Mode Badge
    st.caption(f"👁️ BIO-ADAPTIVE UI: **{current_mode.value.upper()}** ACTIVE")
    
    st.markdown("### 🔮 AI Health Projections")
    
    # 1. Calculate predictions
    tomorrow_readiness = ReadinessForecaster.predict_tomorrow(temp_state)
    burnout_risk, burnout_reason = BurnoutClassifier.assess_risk(temp_state)
    workout_rec = WorkloadRecommender.get_recommendation(temp_state)
    
    # 2. Display Metrics Row
    m1, m2, m3 = st.columns(3)
    
    with m1:
        current_readiness = temp_state.readiness_score
        delta = tomorrow_readiness - current_readiness
        st.metric(
            "Tomorrow's Readiness", 
            f"{tomorrow_readiness}/100", 
            f"{delta:+d}",
            delta_color="normal"
        )
    
    with m2:
        # Color code burnout risk
        risk_color = "normal"
        if burnout_risk in [BurnoutRisk.HIGH, BurnoutRisk.CRITICAL]:
            risk_color = "inverse"
        elif burnout_risk == BurnoutRisk.MODERATE:
            risk_color = "off"
            
        st.metric(
            "Burnout Risk", 
            burnout_risk.value, 
            "⚠️ " + burnout_reason if burnout_risk != BurnoutRisk.LOW else "Stable",
            delta_color=risk_color
        )
        
    with m3:
        st.metric(
            "Rec. Intensity",
            workout_rec.intensity,
            "AI Adaptive"
        )
        
    # --- SIDE-BY-SIDE: Transmission + AI Recommendation ---
    # Generate message
    title, message = FutureSelfAgent.generate_message(temp_state)
    
    # Create two columns for side-by-side layout
    trans_col, rec_col = st.columns([1, 1])
    
    with trans_col:
        # Render Transmission Card (Compact)
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 95, 70, 0.2) 100%);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 12px 14px;
            height: 100%;
            min-height: 120px;
        ">
            <div style="font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1.5px; color: #10b981; margin-bottom: 6px; display: flex; align-items: center; gap: 6px;">
                <span style="animation: pulse 2s infinite;">●</span> INCOMING TRANSMISSION // T-MINUS 7 DAYS
            </div>
            <h4 style="margin: 0 0 6px 0; color: #fff; font-size: 1rem; font-weight: 600;">⚓ {title}</h4>
            <p style="margin: 0; color: #a0e0c0; font-family: 'Courier New', monospace; font-size: 0.8rem; line-height: 1.4;">
                "{message}"
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with rec_col:
        # Recommendation Card (Compact)
        st.markdown(f"""
        <div style="
            background: rgba(59, 130, 246, 0.08);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-left: 3px solid #3b82f6;
            border-radius: 12px;
            padding: 12px 14px;
            height: 100%;
            min-height: 120px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
                <span style="font-size: 0.75rem; color:#3b82f6; font-weight: 600;">🤖 AI RECOMMENDED</span>
                <span style="background:rgba(59,130,246,0.15); color:#60a5fa; padding:2px 6px; border-radius:4px; font-size:0.7rem; font-weight: 600;">
                    {workout_rec.duration_minutes} min
                </span>
            </div>
            <h4 style="margin:0 0 6px 0; color:#fff; font-size: 1rem; font-weight: 600;">{workout_rec.activity_type}</h4>
            <p style="margin:0; color: #93c5fd; font-size:0.8rem; line-height: 1.4;">
                <em>"{workout_rec.reasoning}"</em>
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📊 Current State")
        
        # State metrics
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <div class="state-label">Sleep</div>
                <div class="state-value">{inputs['sleep_hours']}h</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <div class="state-label">Stress</div>
                <div class="state-value">{inputs['stress_level'].title()}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <div class="state-label">Energy</div>
                <div class="state-value">{inputs['energy_level']}/10</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <div class="state-label">Time Available</div>
                <div class="state-value">{inputs['time_available']}h</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Run button
        if st.button("🔮 Run Agent Decision", type="primary", use_container_width=True):
            run_agent_decision(inputs)
    
    with col2:
        # Info box
        st.markdown("""
        <div class="info-box">
            <span>💡</span>
            <span>Adjust your inputs and click 'Run Agent Decision' to see the agent in action!</span>
        </div>
        """, unsafe_allow_html=True)
        
        # How it works
        st.markdown("### 💡 How it works")
        st.markdown("""
        1. **State Analyzer** reads your wearable data and context
        2. **Constraint Evaluator** identifies what's limiting you today
        3. **Trade-Off Engine** prioritizes tasks using a dynamic priority matrix
        4. **Plan Adjuster** modifies future plans based on patterns
        
        The agent makes **autonomous decisions** about what to prioritize, downgrade, or skip - with full **reasoning transparency**.
        """)
    
    # Show decision results if available
    if st.session_state.last_decision:
        st.markdown("---")
        render_decision_results()


def run_agent_decision(inputs):
    """Run the agent decision pipeline."""
    with st.spinner("🤖 Agent analyzing your state..."):
        # Create orchestrator if needed
        if not st.session_state.orchestrator:
            st.session_state.orchestrator = HTPAOrchestrator()
        
        # Generate wearable data
        generator = SyntheticDataGenerator(seed=random.randint(1, 1000))
        
        # Calculate fatigue/stress factors from inputs
        fatigue_factor = 1 - (inputs['energy_level'] / 10)
        stress_map = {"low": 0.2, "medium": 0.5, "high": 0.8}
        stress_factor = stress_map.get(inputs['stress_level'], 0.5)
        
        wearable = generator.generate_wearable_data(
            date=datetime.now(),
            fatigue_factor=fatigue_factor,
            stress_factor=stress_factor
        )
        
        # Override with user inputs
        wearable.sleep_hours = inputs['sleep_hours']
        
        st.session_state.wearable_data = wearable
        
        # Build planned tasks based on checkboxes
        all_tasks = create_sample_planned_tasks()
        tasks = []
        task_mapping = {
            "hiit": "HIIT Workout",
            "meal": "Meal Prep", 
            "sleep": "Sleep Optimization",
            "meditation": "Meditation Session"
        }
        
        for key, enabled in inputs['tasks'].items():
            if enabled:
                for t in all_tasks:
                    if task_mapping.get(key) in t.name:
                        tasks.append(t)
                        break
        
        if not tasks:
            tasks = all_tasks  # Default to all if none selected
        
        # Run decision
        stress = StressLevel(inputs['stress_level'])
        decision = st.session_state.orchestrator.run_daily_decision(
            wearable_data=wearable,
            time_available_hours=inputs['time_available'],
            planned_tasks=tasks,
            user_stress=stress,
            user_energy=inputs['energy_level']
        )
        
        st.session_state.last_decision = decision
        st.session_state.decision_history.append(decision)
        
        # Update chat agent context
        st.session_state.chat_agent.update_context(
            state=st.session_state.orchestrator.current_state,
            decision=decision,
            history=st.session_state.decision_history
        )
        
        # Update adherence score
        prioritized = sum(1 for d in decision.decisions if d.action.value in ["PRIORITIZE", "MAINTAIN"])
        total = len(decision.decisions)
        if total > 0:
            st.session_state.adherence_score = min(100, 70 + int(30 * prioritized / total))
    
    st.success("✅ Decision complete!")
    st.rerun()


def render_decision_results():
    """Render the decision results."""
    decision = st.session_state.last_decision
    state = st.session_state.orchestrator.current_state
    
    st.markdown("### 🤖 Agent Decision Results")
    
    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Readiness Score", f"{state.readiness_score}/100")
    with m2:
        st.metric("Sleep Quality", f"{state.sleep_quality:.0f}/100")
    with m3:
        st.metric("Active Constraints", len(decision.constraints_active))
    with m4:
        st.metric("Confidence", f"{decision.confidence_score:.0%}")
    
    # Decision cards
    st.markdown("#### Domain Decisions")
    
    cols = st.columns(2)
    for i, d in enumerate(decision.decisions):
        with cols[i % 2]:
            action = d.action.value
            domain = d.domain.value.title()
            
            action_styles = {
                "PRIORITIZE": ("✅", "#10b981", "prioritize"),
                "MAINTAIN": ("✓", "#3b82f6", "maintain"),
                "DOWNGRADE": ("↓", "#f59e0b", "downgrade"),
                "DEFER": ("→", "#8b5cf6", "maintain"),
                "SKIP": ("✗", "#ef4444", "skip")
            }
            
            icon, color, css_class = action_styles.get(action, ("?", "#888", ""))
            task_name = d.original_task.name if d.original_task else "N/A"
            
            st.markdown(f"""
            <div class="decision-card {css_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 600; font-size: 1.1rem;">{domain}</div>
                    <span style="color: {color}; font-weight: 600;">{icon} {action}</span>
                </div>
                <div style="margin-top: 8px; opacity: 0.8;">{task_name}</div>
                <div style="font-size: 0.9rem; margin-top: 8px; opacity: 0.6;">{d.reasoning}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Reasoning summary
    st.markdown("#### 💭 Reasoning Summary")
    st.info(decision.reasoning_summary)
    
    # LLM explanation
    if st.session_state.orchestrator.last_llm_explanation:
        with st.expander("🧠 Detailed AI Explanation"):
            st.markdown(st.session_state.orchestrator.last_llm_explanation)


def render_simulation():
    """Render the 7-Day Simulation tab."""
    st.markdown("### 📅 7-Day Simulation")
    st.markdown("Watch the agent make autonomous decisions over a full week")
    
    # Info box
    st.markdown("""
    <div class="info-box blue">
        <span>💡</span>
        <span>Select a recovery profile and run the analysis to see the agent adapt.</span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Scenario dropdown
        st.markdown("**Scenario**")
        scenario = st.selectbox(
            "Scenario",
            [
                "🔥 Burnout → Recovery",
                "📉 Gradual Burnout",
                "🏃 Weekend Warrior",
                "⭐ High Performer"
            ],
            label_visibility="collapsed"
        )
        
        # Daily time slider
        st.markdown("**Daily Time (hours)**")
        daily_time = st.slider("Daily Time", 0.5, 4.0, 2.0, 0.5, label_visibility="collapsed")
        
        # Run button
        if st.button("▶️ Run 7-Day Simulation", type="primary", use_container_width=True):
            run_simulation(scenario, daily_time)
    
    with col2:
        st.markdown("**Available Profiles:**")
        profiles = [
            ("🔥 Burnout → Recovery", "Rehabilitate from high stress state"),
            ("📉 Gradual Burnout", "Preventive intervention demonstration"),
            ("🏃 Weekend Warrior", "Optimization for irregular schedules"),
            ("⭐ High Performer", "Peak performance maintenance")
        ]
        
        for name, desc in profiles:
            st.markdown(f"• **{name}**: {desc}")
    
    # Show simulation results
    if st.session_state.simulation_results:
        st.markdown("---")
        render_simulation_results()


def run_simulation(scenario, daily_time):
    """Run a 7-day simulation."""
    with st.spinner("🔄 Running 7-day simulation..."):
        try:
            from src.simulation.week_simulator import WeekSimulator
            
            # Map scenario to profile
            profile_map = {
                "🔥 Burnout → Recovery": "burnout_recovery",
                "📉 Gradual Burnout": "gradual_burnout",
                "🏃 Weekend Warrior": "weekend_warrior",
                "⭐ High Performer": "high_performer"
            }
            
            profile = profile_map.get(scenario, "burnout_recovery")
            
            # Run simulation
            simulator = WeekSimulator()
            results = simulator.run_week(profile=profile, daily_time_hours=daily_time)
            
            st.session_state.simulation_results = results
        except Exception as e:
            st.error(f"Simulation error: {e}")
            return
    
    st.success("✅ Simulation complete!")
    st.rerun()


def render_simulation_results():
    """Render simulation results."""
    results = st.session_state.simulation_results
    
    st.markdown("### 📊 Simulation Results")
    
    # Summary metrics
    if results and "days" in results:
        days = results["days"]
        
        # Create a simple visualization
        cols = st.columns(7)
        for i, day in enumerate(days[:7]):
            with cols[i]:
                day_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i]
                readiness = day.get("readiness", 50)
                color = "#10b981" if readiness >= 70 else "#f59e0b" if readiness >= 40 else "#ef4444"
                
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="font-weight: 600;">{day_name}</div>
                    <div style="font-size: 1.5rem; color: {color}; margin: 5px 0;">{readiness}</div>
                    <div style="font-size: 0.7rem; opacity: 0.7;">Readiness</div>
                </div>
                """, unsafe_allow_html=True)


def render_chat():
    """Render the Chat tab."""
    st.markdown("### 💬 Chat with HTPA")
    st.markdown("Ask questions about your health decisions or get personalized advice")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").markdown(msg["content"])
        else:
            st.chat_message("assistant").markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your health decisions..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        response = st.session_state.chat_agent.chat(prompt)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    # Quick questions
    st.markdown("---")
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Why skip my workout?"):
            quick_chat("Why did you suggest skipping my workout?")
    with col2:
        if st.button("What should I focus on?"):
            quick_chat("What should I focus on today?")
    with col3:
        if st.button("How am I doing?"):
            quick_chat("How am I doing this week?")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.chat_agent.clear_history()
        st.rerun()


def quick_chat(question):
    """Handle quick chat questions."""
    st.session_state.chat_history.append({"role": "user", "content": question})
    response = st.session_state.chat_agent.chat(question)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()


def render_history():
    """Render the History tab."""
    st.markdown("### 📈 Decision History")
    
    if not st.session_state.decision_history:
        st.info("No decisions recorded yet. Go to **Make Decision** to get started!")
        return
    
    # Summary stats
    total = len(st.session_state.decision_history)
    action_counts = {"PRIORITIZE": 0, "MAINTAIN": 0, "DOWNGRADE": 0, "SKIP": 0}
    
    for decision in st.session_state.decision_history:
        for d in decision.decisions:
            action_counts[d.action.value] = action_counts.get(d.action.value, 0) + 1
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Decisions", total)
    col2.metric("Prioritized", action_counts["PRIORITIZE"])
    col3.metric("Downgraded", action_counts["DOWNGRADE"])
    col4.metric("Skipped", action_counts["SKIP"])
    
    st.markdown("---")
    
    # Decision list
    for decision in reversed(st.session_state.decision_history[-10:]):
        with st.expander(f"Decision {decision.decision_id} - {decision.timestamp.strftime('%Y-%m-%d %H:%M')}"):
            st.markdown(f"**Constraints:** {', '.join(decision.constraints_active) or 'None'}")
            st.markdown(f"**Confidence:** {decision.confidence_score:.0%}")
            
            for d in decision.decisions:
                action_icon = {"PRIORITIZE": "✅", "MAINTAIN": "✓", "DOWNGRADE": "↓", "SKIP": "✗"}.get(d.action.value, "?")
                st.markdown(f"{action_icon} **{d.domain.value.title()}**: {d.action.value} - _{d.reasoning}_")


def render_adaptation():
    """Render the Adaptation tab."""
    st.markdown("### 🔄 Adaptation Patterns")
    st.markdown("View how the agent learns and adapts over time")
    
    if not st.session_state.orchestrator:
        st.info("Run some decisions first to see adaptation patterns!")
        return
    
    # Get adaptation report
    try:
        report = st.session_state.orchestrator.get_adaptation_report()
        
        if report:
            st.markdown("#### Detected Patterns")
            for pattern in report.get("patterns", []):
                st.markdown(f"• **{pattern['name']}**: {pattern['description']}")
            
            st.markdown("#### Recommended Adjustments")
            for adj in report.get("adjustments", []):
                st.markdown(f"• {adj}")
        else:
            st.info("Not enough data yet to detect patterns. Keep using the system!")
    except Exception as e:
        st.info("Adaptation analysis will be available after more decisions are made.")


def render_about():
    """Render the About tab."""
    st.markdown("### 💎 Equilibra AI")
    
    st.markdown("""
    **Equilibra** is the world's most advanced autonomous health balancing algorithm. 
    It integrates wearable data with your daily constraints to dynamically optimize your schedule.
    """)
    
    st.markdown("### The Equilibra Difference")
    st.markdown("Most health apps just track data. **Equilibra takes action.**")
    
    st.markdown("### Key Capabilities:")
    
    capabilities = [
        ("💎", "Dynamic Trade-Off Engine", "Maximizes long-term health, not just daily streaks"),
        ("😴", "Sleep Debt Management", "Proactively clears sleep debt before it affects performance"),
        ("🧠", "Context-Aware Coaching", "Understands when you're stressed vs. lazy"),
        ("🔒", "Privacy First", "All processing happens securely")
    ]
    
    for icon, title, desc in capabilities:
        st.markdown(f"• {icon} **{title}**: {desc}")
    
    st.markdown("### Architecture")
    st.markdown("Built on a sophisticated multi-agent system:")
    
    st.markdown("""
    <div class="architecture-box">
    Wearable Data → State Analyzer → Constraint Eval → Trade-Off Engine → Plan Adjuster<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;LLM Reasoner
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Version:** 2.0.0 Professional")
    
    if st.button("📥 Export Health Report"):
        if st.session_state.orchestrator:
            path = st.session_state.orchestrator.export_session()
            st.success(f"Exported to: {path}")
        else:
            st.warning("Run some decisions first!")


# Main app
def main():
    # Get sidebar inputs
    inputs = render_sidebar()
    
    # Render header with settings
    render_header()
    
    # Tab navigation
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Make Decision",
        "📅 7-Day Simulation", 
        "💬 Chat",
        "📈 History",
        "🔄 Adaptation",
        "ℹ️ About"
    ])
    
    with tab1:
        render_make_decision(inputs)
    
    with tab2:
        render_simulation()
    
    with tab3:
        render_chat()
    
    with tab4:
        render_history()
    
    with tab5:
        render_adaptation()
    
    with tab6:
        render_about()


if __name__ == "__main__":
    main()
