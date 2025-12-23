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

# Force reload config for hot-swap
try:
    from dotenv import load_dotenv
    import src.core.config
    load_dotenv(override=True)
    if os.getenv("GROQ_API_KEY"):
        src.core.config.set_groq_key(os.getenv("GROQ_API_KEY"), os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
except Exception:
    pass

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
from src.agents.burnout_predictor import BurnoutPredictor, BurnoutForecast
from src.agents.health_council import HealthCouncil, ConsensusDecision
from src.agents.temporal_reasoner import TemporalReasoner, TemporalInsight
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
# User data persistence - Session-specific files (best of both worlds)
import json
import base64
import hashlib
import uuid

def get_session_id():
    """Get or create a session ID using URL query params (persists across refreshes)."""
    # Check if session_id is in URL query params
    query_params = st.query_params
    
    if "sid" in query_params:
        # Use existing session ID from URL
        return query_params["sid"]
    else:
        # Generate new session ID and add to URL
        new_sid = str(uuid.uuid4())[:8]  # Short ID
        st.query_params["sid"] = new_sid
        return new_sid

def get_cache_file():
    """Get the cache file path for this session."""
    session_id = get_session_id()
    # Use hash of session ID for filename
    filename = hashlib.md5(session_id.encode()).hexdigest()
    cache_dir = os.path.join(os.path.dirname(__file__), ".cache")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"{filename}.json")

def save_to_cache(data: dict):
    """Save user data to session-specific cache file."""
    try:
        cache_file = get_cache_file()
        with open(cache_file, 'w') as f:
            json.dump(data, f)
    except:
        pass

def load_from_cache():
    """Load user data from session-specific cache file."""
    try:
        cache_file = get_cache_file()
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def persist_session_data():
    """Helper to save all persistent session data to cache."""
    if "onboarding_complete" in st.session_state and st.session_state.onboarding_complete:
        data = {
            "onboarding_complete": True,
            "user_name": st.session_state.get("user_name", ""),
            "user_age": st.session_state.get("user_age", 25),
            "user_goal": st.session_state.get("user_goal", ""),
        }
        save_to_cache(data)

def deserialize_decisions(data_list):
    """Reconstruct TradeOffDecision objects from JSON dicts."""
    decisions = []
    try:
        from src.models import TradeOffDecision, DomainDecision, PlannedTask, FutureImpact, HealthDomain, DecisionAction
        
        for d_dict in data_list:
            # Reconstruct Nested DomainDecisions
            domain_decisions = []
            for dd in d_dict.get("decisions", []):
                # Reconstruct tasks
                orig_task = None
                if dd.get("original"):
                    t = dd["original"]
                    orig_task = PlannedTask(
                        domain=HealthDomain(t["domain"]),
                        name=t["name"],
                        duration_minutes=t["duration_minutes"],
                        intensity=t["intensity"],
                        description=t["description"]
                    )
                
                adj_task = None
                if dd.get("adjusted"):
                    t = dd["adjusted"]
                    adj_task = PlannedTask(
                        domain=HealthDomain(t["domain"]),
                        name=t["name"],
                        duration_minutes=t["duration_minutes"],
                        intensity=t["intensity"],
                        description=t["description"]
                    )
                
                domain_decisions.append(DomainDecision(
                    domain=HealthDomain(dd["domain"]),
                    action=DecisionAction(dd["action"]),
                    original_task=orig_task,
                    adjusted_task=adj_task,
                    reasoning=dd["reasoning"],
                    priority_score=dd.get("priority_score", 0.0)
                ))

            # Future impacts
            future_impacts = []
            for fi in d_dict.get("future_impacts", []):
                future_impacts.append(FutureImpact(
                    days_affected=fi["days_affected"],
                    adjustment_type=fi["type"],
                    description=fi["description"]
                ))
            
            # Main object
            tod = TradeOffDecision(
                decision_id=d_dict["decision_id"],
                timestamp=datetime.fromisoformat(d_dict["timestamp"]),
                state_snapshot=d_dict.get("state_snapshot", {}),
                constraints_active=d_dict.get("constraints_active", []),
                priority_adjustments=d_dict.get("priority_adjustments", {}),
                decisions=domain_decisions,
                future_impacts=future_impacts,
                confidence_score=d_dict.get("confidence_score", 0.8),
                reasoning_summary=d_dict.get("reasoning_summary", "")
            )
            decisions.append(tod)
    except Exception as e:
        # If deserialization fails, return empty list to avoid crashes
        return []
    
    return decisions

# Initialize session state
def init_session_state():
    # Session-based storage with file cache per session
    
    # Load cached data for this session
    cached = load_from_cache()
    
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    if "last_decision" not in st.session_state:
        st.session_state.last_decision = None
    if "chat_agent" not in st.session_state:
        st.session_state.chat_agent = get_chat_agent()
    else:
        # Hot-fix: Update existing agent if key became available
        agent = st.session_state.chat_agent
        new_key = os.getenv("GROQ_API_KEY")
        if new_key and (getattr(agent, 'client', None) is None or getattr(agent, 'api_key', None) != new_key):
            agent.api_key = new_key
            agent.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            try:
                from groq import Groq
                agent.client = Groq(api_key=new_key)
            except ImportError:
                pass
    
    # Load chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
            
    if "wearable_data" not in st.session_state:
        st.session_state.wearable_data = None
        
    # Load decision history (session-only)
    if "decision_history" not in st.session_state:
        st.session_state.decision_history = []
            
    if "adherence_score" not in st.session_state:
        st.session_state.adherence_score = 85
        
    # Streak Logic (session-only)
    if "streak_count" not in st.session_state:
        st.session_state.streak_count = 0
        st.session_state.last_active_date = None
        
        # Calculate daily streak
        today_str = datetime.now().date().isoformat()
        if st.session_state.last_active_date != today_str:
            yesterday_str = (datetime.now().date() - timedelta(days=1)).isoformat()
            if st.session_state.last_active_date == yesterday_str:
                 st.session_state.streak_count += 1
            else:
                 st.session_state.streak_count = 1 # Start new streak
            
            st.session_state.last_active_date = today_str
            # Save will happen on next persist trigger
        
    # Crisis Mode Detection
    if "burnout_predictor" not in st.session_state:
        st.session_state.burnout_predictor = BurnoutPredictor()
    
    # Multi-Agent System
    if "health_council" not in st.session_state:
        st.session_state.health_council = HealthCouncil()
    
    if "temporal_reasoner" not in st.session_state:
        st.session_state.temporal_reasoner = TemporalReasoner()
    
    if "crisis_mode" not in st.session_state:
        st.session_state.crisis_mode = False
        st.session_state.burnout_forecast = None
        
    if "simulation_results" not in st.session_state:
        st.session_state.simulation_results = None
    
    # Skip onboarding for hackathon - go straight to app
    if "onboarding_complete" not in st.session_state:
        st.session_state.onboarding_complete = True  # Always complete
        st.session_state.user_name = "Demo User"
        st.session_state.user_age = 25
        st.session_state.user_goal = "Improve overall health"
            
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = 1
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Demo User"
    if "user_age" not in st.session_state:
        st.session_state.user_age = 25
    if "user_goal" not in st.session_state:
        st.session_state.user_goal = "Improve overall health"


init_session_state()


def get_theme_css():
    """Generate CSS for the app styling with premium dark mode enforced."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * { 
            font-family: 'Inter', sans-serif; 
            -webkit-tap-highlight-color: transparent;
        }
        
        /* Mobile-first base */
        html {
            font-size: 16px;
            -webkit-text-size-adjust: 100%;
        }
        
        /* Main app - premium dark gradient */
        .stApp {
            background: linear-gradient(135deg, #0d0d0d 0%, #1a1a2e 40%, #16213e 70%, #0f3460 100%);
        }
        
        /* Mobile-first container */
        .main .block-container {
            padding: 1rem 1rem !important;
            max-width: 100% !important;
        }
        
        /* Desktop: wider container */
        @media (min-width: 768px) {
            .main .block-container {
                padding: 1rem 2rem !important;
                max-width: 900px !important;
            }
        }
        
        /* Hide hamburger menu on mobile - use bottom nav instead */
        @media (max-width: 768px) {
            [data-testid="stSidebar"] {
                display: none !important;
            }
            
            /* Reduce header spacing */
            .main .block-container {
                padding-top: 0.5rem !important;
            }
            
            /* Stack columns on mobile */
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
            }
            
            /* Larger touch targets for buttons */
            .stButton > button {
                min-height: 48px !important;
                font-size: 1rem !important;
            }
            
            /* Tabs scrollable on mobile */
            .stTabs [data-baseweb="tab-list"] {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }
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
        st.markdown("### 👤 Your Profile")
        
        # Age slider
        st.markdown("**Age**")
        age = st.slider(
            "Age", 18, 80, st.session_state.user_age,
            label_visibility="collapsed",
            key="age_slider"
        )
        st.session_state.user_age = age
        
        # Goal selection
        st.markdown("**Primary Goal**")
        goals = [
            "Improve overall health",
            "Lose weight",
            "Build muscle",
            "Reduce stress",
            "Better sleep",
            "Increase energy"
        ]
        goal = st.selectbox(
            "Goal",
            goals,
            index=goals.index(st.session_state.user_goal) if st.session_state.user_goal in goals else 0,
            label_visibility="collapsed",
            key="goal_select"
        )
        st.session_state.user_goal = goal
        
        st.markdown("---")
        
        st.markdown("### 📊 Today's Signals")
        
        # Load Scenario dropdown
        st.markdown("**Load Scenario**")
        scenario = st.selectbox(
            "Load Scenario",
            ["Custom", "Well Rested", "Sleep Deprived", "High Stress", "Time Crunch", "Recovery Day"],
            label_visibility="collapsed"
        )
        
        # Apply scenario presets - check feeling picker first, then dropdown
        if "scenario_sleep" in st.session_state:
            # Values from feeling picker buttons take priority
            default_sleep = st.session_state.scenario_sleep
            default_energy = st.session_state.scenario_energy
            default_stress = st.session_state.scenario_stress.lower()
            default_time = st.session_state.scenario_time
        elif scenario == "Well Rested":
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
        
        # === CIRCUIT BREAKER LITE ===
        # Detect critical biological state
        is_sleep_critical = sleep_hours < 5.5
        is_energy_critical = energy_level <= 3
        is_stress_critical = stress_level.lower() == "high"
        
        # Determine if high-intensity activities should be blocked
        # Block if biology is critical OR crisis mode is active
        biology_blocked = is_sleep_critical or is_energy_critical or (is_stress_critical and energy_level <= 5) or st.session_state.crisis_mode
        
        # Planned Tasks with Circuit Breaker
        st.markdown("### 📋 Planned Tasks")
        
        # Show Circuit Breaker status
        if biology_blocked:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(127, 29, 29, 0.2) 100%);
                border: 1px solid rgba(239, 68, 68, 0.4);
                border-radius: 8px;
                padding: 10px 12px;
                margin-bottom: 12px;
            ">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.2rem;">🛡️</span>
                    <div>
                        <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; color: #ef4444; font-weight: 600;">
                            CIRCUIT BREAKER ACTIVE
                        </div>
                        <div style="font-size: 0.8rem; color: #fca5a5; margin-top: 2px;">
                            High-intensity blocked by your biology
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # HIIT - Blocked when in critical state
        if biology_blocked:
            st.markdown("""
            <div style="
                background: rgba(75, 75, 75, 0.3);
                border: 1px solid rgba(100, 100, 100, 0.3);
                border-radius: 8px;
                padding: 10px 12px;
                margin-bottom: 8px;
                opacity: 0.6;
                cursor: not-allowed;
            ">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1rem; filter: grayscale(100%);">🏋️</span>
                        <span style="color: #888; text-decoration: line-through;">HIIT Workout (45min)</span>
                    </div>
                    <span style="font-size: 0.65rem; background: rgba(239, 68, 68, 0.2); color: #f87171; padding: 2px 6px; border-radius: 4px;">
                        🚫 BLOCKED
                    </span>
                </div>
                <div style="font-size: 0.7rem; color: #ef4444; margin-top: 4px; font-style: italic;">
                    "This action is blocked by your biology."
                </div>
            </div>
            """, unsafe_allow_html=True)
            task1 = False  # Force disabled
        else:
            task1 = st.checkbox("🏋️ HIIT Workout (45min)", value=True, key="task_hiit")
        
        # Other tasks remain available
        task2 = st.checkbox("🥗 Meal Prep (60min)", value=True, key="task_meal")
        task3 = st.checkbox("😴 Sleep Routine (30min)", value=True, key="task_sleep")
        task4 = st.checkbox("🧘 Meditation (20min)", value=True, key="task_meditation")
        
        # Show what's recommended when blocked
        if biology_blocked:
            st.markdown("""
            <div style="
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 8px;
                padding: 8px 10px;
                margin-top: 8px;
            ">
                <div style="font-size: 0.7rem; color: #10b981;">
                    💡 <strong>Equilibra recommends:</strong> Rest, light activity, or recovery today.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        return {
            "sleep_hours": sleep_hours,
            "energy_level": energy_level,
            "stress_level": stress_level.lower(),
            "time_available": time_available,
            "biology_blocked": biology_blocked,
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
        streak = st.session_state.get("streak_count", 1)
        change = "+2%" if score >= 80 else "-1%"
        change_color = "#10b981" if "+" in change else "#ef4444"
        
        st.markdown(f"""
        <div style="text-align: right;">
            <div style="font-size: 0.75rem; opacity: 0.7; display:flex; justify-content:flex-end; gap:6px; align-items:center;">
                <span>Adherence Score</span>
                <span style="background:rgba(245, 158, 11, 0.2); color:#f59e0b; padding:1px 6px; border-radius:10px; font-weight:600;">🔥 {streak}</span>
            </div>
            <div style="font-size: 2rem; font-weight: 600;">{score}%</div>
            <div style="font-size: 0.8rem; color: {change_color};">↑ {change}</div>
        </div>
        """, unsafe_allow_html=True)


def render_feeling_picker():
    """Render friendly 'How are you feeling?' scenario buttons."""
    
    # Scenario presets
    scenarios = {
        "😴 Exhausted": {"sleep": 4.0, "energy": 2, "stress": "High", "time": 1.0},
        "😰 Stressed": {"sleep": 6.0, "energy": 4, "stress": "High", "time": 2.0},
        "😊 Balanced": {"sleep": 7.0, "energy": 6, "stress": "Medium", "time": 3.0},
        "⚡ Energized": {"sleep": 8.0, "energy": 8, "stress": "Low", "time": 4.0},
        "🔥 Peak": {"sleep": 9.0, "energy": 10, "stress": "Low", "time": 5.0},
    }
    
    st.markdown("""
    <div style="
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 16px;
    ">
        <div style="font-size: 0.8rem; color: #888; margin-bottom: 8px;">
            👋 How are you feeling today?
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create button columns
    cols = st.columns(5)
    
    for idx, (label, values) in enumerate(scenarios.items()):
        with cols[idx]:
            if st.button(label, key=f"scenario_{label}", use_container_width=True):
                # Update session state with scenario values
                st.session_state.scenario_sleep = values["sleep"]
                st.session_state.scenario_energy = values["energy"]
                st.session_state.scenario_stress = values["stress"]
                st.session_state.scenario_time = values["time"]
                st.session_state.scenario_active = label
                st.rerun()
    
    # Show active scenario
    if "scenario_active" in st.session_state:
        st.markdown(f"""
        <div style="
            text-align: center;
            font-size: 0.75rem;
            color: #10b981;
            margin-top: 8px;
        ">
            ✓ {st.session_state.scenario_active} mode active
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

    # === COMPACT CALENDAR WITH CIRCUIT BREAKER ===
    from datetime import datetime
    today = datetime.now().strftime("%A, %b %d")
    is_critical = inputs.get('biology_blocked', False)
    
    # Compact header with circuit breaker indicator
    st.markdown("""
    <div style="border-top: 1px solid rgba(255,255,255,0.1); margin: 16px 0 12px 0;"></div>
    """, unsafe_allow_html=True)
    
    if is_critical:
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 0.9rem; font-weight: 600; color: #fff;">📅 Today's Schedule</span>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 0.6rem; background: rgba(239, 68, 68, 0.15); color: #f87171; padding: 3px 8px; border-radius: 10px; font-weight: 600;">
                    🛡️ CIRCUIT BREAKER
                </span>
                <span style="font-size: 0.7rem; color: #888;">{today}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 0.9rem; font-weight: 600; color: #fff;">📅 Today's Schedule</span>
            <span style="font-size: 0.7rem; color: #888;">{today}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Mock calendar events - compact list
    calendar_events = [
        {"time": "6:30", "title": "HIIT", "type": "high_intensity", "icon": "🏋️"},
        {"time": "8:00", "title": "Standup", "type": "work", "icon": "💼"},
        {"time": "12:00", "title": "Lunch Walk", "type": "recovery", "icon": "🚶"},
        {"time": "3:00", "title": "Deep Work", "type": "cognitive", "icon": "🧠"},
        {"time": "6:00", "title": "Evening Run", "type": "high_intensity", "icon": "🏃"},
        {"time": "9:00", "title": "Wind-Down", "type": "recovery", "icon": "🌙"},
    ]
    
    blocked_types = ["high_intensity", "cognitive"] if is_critical else []
    
    # Create 3-column grid for 2 rows
    row1_cols = st.columns(3)
    row2_cols = st.columns(3)
    all_cols = row1_cols + row2_cols
    
    for idx, event in enumerate(calendar_events):
        is_blocked = event["type"] in blocked_types
        event_key = f"override_{event['title'].replace(' ', '_')}"
        
        if event_key not in st.session_state:
            st.session_state[event_key] = False
        
        with all_cols[idx]:
            if is_blocked and not st.session_state[event_key]:
                # Blocked event - compact card
                st.markdown(f"""
                <div style="
                    background: rgba(239, 68, 68, 0.06);
                    border: 1px solid rgba(239, 68, 68, 0.2);
                    border-radius: 8px;
                    padding: 8px 10px;
                    opacity: 0.6;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.65rem; color: #888;">{event['time']}</span>
                        <span style="font-size: 0.55rem; background: rgba(239, 68, 68, 0.2); color: #f87171; padding: 1px 4px; border-radius: 3px;">🚫</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #666; text-decoration: line-through; margin-top: 2px;">
                        {event['icon']} {event['title']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Tiny override link
                if st.button("Override?", key=f"btn_{event_key}", help="Click to override"):
                    st.session_state[event_key + "_explain"] = True
                
                if st.session_state.get(event_key + "_explain", False):
                    st.caption("⚠️ Override not recommended")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✓", key=f"yes_{event_key}", help="Override"):
                            st.session_state[event_key] = True
                            st.session_state[event_key + "_explain"] = False
                            st.rerun()
                    with c2:
                        if st.button("✕", key=f"no_{event_key}", help="Cancel"):
                            st.session_state[event_key + "_explain"] = False
                            st.rerun()
            
            elif is_blocked and st.session_state[event_key]:
                # Override active - amber card
                st.markdown(f"""
                <div style="
                    background: rgba(251, 191, 36, 0.08);
                    border: 1px solid rgba(251, 191, 36, 0.3);
                    border-radius: 8px;
                    padding: 8px 10px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.65rem; color: #fbbf24;">{event['time']}</span>
                        <span style="font-size: 0.55rem; background: rgba(251, 191, 36, 0.2); color: #fbbf24; padding: 1px 4px; border-radius: 3px;">⚠️</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #fcd34d; margin-top: 2px;">
                        {event['icon']} {event['title']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            else:
                # Normal event - clean card
                st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.06);
                    border-radius: 8px;
                    padding: 8px 10px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.65rem; color: #888;">{event['time']}</span>
                        <span style="font-size: 0.55rem; color: #10b981;">✓</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #fff; margin-top: 2px;">
                        {event['icon']} {event['title']}
                    </div>
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
            
        # Save session data
        persist_session_data()
    
    st.success("✅ Decision complete!")
    st.rerun()


def render_decision_results():
    """Render the decision results."""
    if not st.session_state.get("last_decision") or not st.session_state.get("orchestrator"):
        return
    
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
            raw_results = simulator.run_simulation(days=7, time_available_hours=daily_time)
            
            # Process results for visualization
            processed_days = []
            for r in raw_results:
                metrics = r.wearable_summary
                
                # Approximate levels from metrics since they aren't directly in summary
                # Energy approximated from readiness and sleep
                energy = max(1, min(10, int(metrics.get("readiness_score", 50) / 10)))
                
                # Stress approximated from HRV (lower HRV = higher stress)
                # HRV 20-100 map to Stress 1.0-0.0 roughly
                hrv = metrics.get("hrv_ms", 50)
                stress = max(0.1, min(1.0, 1.0 - (hrv / 120.0)))
                
                processed_days.append({
                    "day": r.day,
                    "date": r.date.strftime("%Y-%m-%d"),
                    "readiness": metrics.get("readiness_score", 50),
                    "energy_level": energy,
                    "stress_level": stress,
                    "metrics": metrics
                })
            
            st.session_state.simulation_results = {"days": processed_days}
        except Exception as e:
            st.error(f"Simulation error: {e}")
            import traceback
            st.error(traceback.format_exc())
            return
    
    st.success("✅ Simulation complete!")
    st.rerun()


def render_simulation_results():
    """Render simulation results using Plotly."""
    results = st.session_state.simulation_results
    
    st.markdown("### 📊 Predicted Trends")
    
    if results and "days" in results:
        days = results["days"]
        
        # Prepare data for Plotly
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        dates = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        readiness = [d.get("readiness", 50) for d in days[:7]]
        energy = [d.get("energy_level", 5) * 10 for d in days[:7]] # Scale to 0-100
        stress = [d.get("stress_level", 0.5) * 100 for d in days[:7]] # Scale to 0-100
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add Readiness (Area)
        fig.add_trace(
            go.Scatter(x=dates, y=readiness, name="Readiness", stackgroup='one',
                     line=dict(width=2, color='rgba(16, 185, 129, 0.8)'),
                     fillcolor='rgba(16, 185, 129, 0.1)'),
            secondary_y=False,
        )
        
        # Add Energy (Line)
        fig.add_trace(
            go.Scatter(x=dates, y=energy, name="Energy", 
                     line=dict(width=3, color='#3b82f6')),
            secondary_y=False,
        )
        
        # Add Stress (Bar) - make it subtle
        fig.add_trace(
            go.Bar(x=dates, y=stress, name="Stress Load",
                   marker_color='rgba(239, 68, 68, 0.3)'),
            secondary_y=False,
        )
        
        # Update layout for premium dark look
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0', family="Inter"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified"
        )
        
        fig.update_xaxes(showgrid=False, gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', range=[0, 110])
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Key Insights
        avg_readiness = sum(readiness) / len(readiness)
        lowest_day = dates[readiness.index(min(readiness))]
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-weight: 600; color: #fff; margin-bottom: 8px;">💡 Forecast Insights</div>
            <div style="font-size: 0.9rem; color: #94a3b8;">
                • Average readiness for the week: <span style="color: #10b981;">{avg_readiness:.0f}%</span><br>
                • Lowest point expected on: <span style="color: #f97316;">{lowest_day}</span><br>
                • Recovery protocols effectively manage stress spikes.
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_chat():
    """Render the Chat tab."""
    # Sync latest user profile to agent
    # Sync latest user profile to agent
    if "chat_agent" in st.session_state:
        try:
            st.session_state.chat_agent.update_context(
                user_profile={
                    "name": st.session_state.user_name,
                    "age": st.session_state.user_age,
                    "goal": st.session_state.user_goal,
                    "adherence": st.session_state.get("adherence_score", 85)
                }
            )
        except TypeError:
            # Handle hot-reloading issue where old class instance is in session
            import importlib
            import src.agents.chat_agent
            importlib.reload(src.agents.chat_agent)
            
            # Recreate agent
            old_msgs = st.session_state.chat_agent.messages
            st.session_state.chat_agent = src.agents.chat_agent.ConversationalAgent()
            st.session_state.chat_agent.messages = old_msgs
            
            # Retry update with new instance
            st.session_state.chat_agent.update_context(
                user_profile={
                    "name": st.session_state.user_name,
                    "age": st.session_state.user_age,
                    "goal": st.session_state.user_goal,
                    "adherence": st.session_state.get("adherence_score", 85)
                }
            )
        
    st.markdown("### 💬 Chat with HTPA")
    st.markdown("Ask questions about your health decisions or get personalized advice")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").markdown(msg["content"])
        else:
            st.chat_message("assistant").markdown(msg["content"])
    
    # Voice input with improved error handling
    st.markdown("**🎙️ Voice Message**")
    audio_val = st.audio_input("Record voice message", label_visibility="collapsed")
    
    if audio_val:
        if st.button("📤 Send Voice Message", type="primary", use_container_width=True, key="send_voice"):
            with st.spinner("🎙️ Transcribing..."):
                try:
                    # Get audio bytes
                    audio_bytes = audio_val.getvalue()
                    
                    # Try transcription
                    transcript = st.session_state.chat_agent.transcribe_audio(audio_val)
                    
                    if transcript and len(transcript.strip()) > 0:
                        # Add user message
                        st.session_state.chat_history.append({"role": "user", "content": f"🎤 {transcript}"})
                        
                        # Get AI response
                        response = st.session_state.chat_agent.chat(transcript)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                        
                        # Generate voice response using Groq PlayAI TTS
                        try:
                            from groq import Groq
                            import io
                            
                            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                            
                            # Generate TTS audio using Groq's playai-tts
                            tts_response = client.audio.speech.create(
                                model="playai-tts",
                                voice="Fritz-PlayAI",
                                input=response[:1000],
                                response_format="wav"
                            )
                            
                            # The response is a BinaryAPIResponse, read it as bytes
                            audio_bytes = tts_response.read()
                            
                            # Save audio to session state
                            st.session_state.tts_audio_data = audio_bytes
                            st.session_state.show_tts_player = True
                            
                        except Exception as tts_error:
                            error_msg = str(tts_error)
                            
                            # Check if it's the terms acceptance error
                            if "model_terms_required" in error_msg:
                                st.warning("⚠️ PlayAI TTS requires terms acceptance")
                                st.info("📝 Please accept terms at: https://console.groq.com/playground?model=playai-tts")
                                st.info("💡 Using browser TTS as fallback...")
                            else:
                                st.warning(f"⚠️ TTS failed: {error_msg}")
                            
                            # Fallback to browser TTS
                            st.session_state.last_text_for_speech = response
                            st.session_state.should_speak = True
                        
                        persist_session_data()
                        st.rerun()
                    else:
                        st.warning("⚠️ Transcription returned empty")
                        st.info("Audio might be unclear. Try speaking louder or use text input below.")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💬 Please use text chat below")
    
    # Play Groq TTS audio response
    if st.session_state.get("show_tts_player", False) and st.session_state.get("tts_audio_data"):
        st.markdown("**🔊 AI Voice Response (PlayAI)**")
        st.audio(st.session_state.tts_audio_data, format="audio/wav")
        
        if st.button("✅ Clear Audio", key="clear_tts"):
            st.session_state.show_tts_player = False
            st.session_state.tts_audio_data = None
            st.rerun()
    
    # Fallback: Browser TTS if Groq TTS unavailable
    if st.session_state.get("should_speak", False) and st.session_state.get("last_text_for_speech"):
        text_to_speak = st.session_state.last_text_for_speech[:500]
        safe_text = text_to_speak.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
        
        st.markdown("**🔊 AI Speaking (Browser Voice)...**")
        st.markdown(f"""
        <script>
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance("{safe_text}");
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
        </script>
        """, unsafe_allow_html=True)
        
        if st.button("🔇 Stop Speaking", key="stop_browser_tts"):
            st.markdown("<script>window.speechSynthesis.cancel();</script>", unsafe_allow_html=True)
            st.session_state.should_speak = False
            st.session_state.last_text_for_speech = None
            st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask me anything about your health decisions..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        response = st.session_state.chat_agent.chat(prompt)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        persist_session_data()
        
        st.rerun()
    
    # Quick questions
    st.markdown("---")
    st.markdown("**Quick Actions:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Why skip?", use_container_width=True):
            quick_chat("Why did you suggest skipping my workout?")
    with col2:
        if st.button("Focus?", use_container_width=True):
            quick_chat("What should I focus on today given my state?")
    with col3:
        if st.button("Status?", use_container_width=True):
            quick_chat("How am I doing this week based on my history?")
    with col4:
        # Inspired by "Diet Planner" feature
        if st.button("📅 Plan Week", use_container_width=True):
            quick_chat(f"Generate a personalized weekly schedule plan for me based on my goal: {st.session_state.user_goal}. Format it as a list.")
    
    if st.button("🗑️ Clear Chat", type="secondary"):
        st.session_state.chat_history = []
        st.session_state.chat_agent.clear_history()
        st.rerun()


def quick_chat(question):
    """Handle quick chat questions."""
    st.session_state.chat_history.append({"role": "user", "content": question})
    response = st.session_state.chat_agent.chat(question)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    persist_session_data()
    st.rerun()


def render_history():
    """Render the History tab."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 📈 Decision History")
    with col2:
        view_mode = st.radio("View", ["Cards", "Table"], horizontal=True, label_visibility="collapsed")
    
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
    
    if view_mode == "Table":
        # Raw Data View (Inspired by fitness-tracker)
        data = []
        for d in st.session_state.decision_history:
            for item in d.decisions:
                data.append({
                    "Timestamp": d.timestamp.strftime('%Y-%m-%d %H:%M'),
                    "Domain": item.domain.value,
                    "Action": item.action.value,
                    "Reasoning": item.reasoning,
                    "Confidence": float(d.confidence_score),
                    "Constraints": ", ".join(d.constraints_active)
                })
        
        st.dataframe(
            data, 
            use_container_width=True,
            column_config={
                "Timestamp": st.column_config.TextColumn("Time", width="medium"),
                "Domain": st.column_config.TextColumn("Domain", width="small"),
                "Action": st.column_config.TextColumn("Action", width="small"),
                "Reasoning": st.column_config.TextColumn("Reason", width="large"),
                "Confidence": st.column_config.ProgressColumn("Confidence", format="%.0f%%", min_value=0, max_value=1),
                "Constraints": st.column_config.TextColumn("Active Constraints", width="medium")
            }
        )
    else:
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
    
    if not st.session_state.decision_history or len(st.session_state.decision_history) < 2:
        st.info("📊 Make at least 2 decisions to see adaptation patterns!")
        return
    
    # Analyze decision history
    decisions = st.session_state.decision_history
    
    st.markdown("#### Detected Patterns")
    
    # Pattern 1: Sleep trends
    sleep_hours = [d.state_snapshot.get('sleep_hours', 7) for d in decisions if d.state_snapshot]
    if sleep_hours:
        avg_sleep = sum(sleep_hours) / len(sleep_hours)
        if avg_sleep < 6.5:
            st.markdown(f"• **Sleep Debt Pattern**: Average sleep is {avg_sleep:.1f}h (below optimal 7-8h)")
        elif avg_sleep >= 7.5:
            st.markdown(f"• **Healthy Sleep Pattern**: Consistent {avg_sleep:.1f}h average")
        else:
            st.markdown(f"• **Moderate Sleep Pattern**: {avg_sleep:.1f}h average")
    
    # Pattern 2: Stress trends
    stress_levels = []
    for d in decisions:
        if d.state_snapshot and 'stress_level' in d.state_snapshot:
            level = d.state_snapshot['stress_level']
            if isinstance(level, str):
                stress_levels.append(level.upper())
    
    if stress_levels:
        high_stress_count = stress_levels.count('HIGH')
        if high_stress_count > len(stress_levels) / 2:
            st.markdown(f"• **Chronic Stress Detected**: {high_stress_count}/{len(stress_levels)} decisions under high stress")
        elif high_stress_count > 0:
            st.markdown(f"• **Intermittent Stress**: {high_stress_count}/{len(stress_levels)} high-stress periods")
        else:
            st.markdown("• **Low Stress Pattern**: Stress levels well-managed")
    
    # Pattern 3: Most skipped activities
    skipped_domains = {}
    for d in decisions:
        for domain_dec in d.decisions:
            if domain_dec.action.value == "SKIP":
                domain = domain_dec.domain.value
                skipped_domains[domain] = skipped_domains.get(domain, 0) + 1
    
    if skipped_domains:
        most_skipped = max(skipped_domains, key=skipped_domains.get)
        st.markdown(f"• **Avoidance Pattern**: {most_skipped} skipped {skipped_domains[most_skipped]} times")
    
    st.markdown("---")
    st.markdown("#### Recommended Adjustments")
    
    # Generate recommendations based on patterns
    if sleep_hours and avg_sleep < 6.5:
        st.markdown("• 🛏️ **Prioritize Sleep**: Set a consistent bedtime 30min earlier")
    
    if stress_levels and high_stress_count > len(stress_levels) / 2:
        st.markdown("• 🧘 **Stress Management**: Add daily 10-min meditation to routine")
    
    if skipped_domains and most_skipped in ["Exercise", "Fitness"]:
        st.markdown("• 🏃 **Movement Strategy**: Try shorter, 15-min workouts instead of skipping")
    
    # Burnout risk recommendation
    if st.session_state.burnout_forecast and st.session_state.burnout_forecast.risk_score > 50:
        st.markdown(f"• ⚠️ **Crisis Prevention**: Current burnout risk is {st.session_state.burnout_forecast.risk_score}% - schedule recovery day")
    
    if not (sleep_hours and avg_sleep < 6.5) and not (stress_levels and high_stress_count > len(stress_levels) / 2):
        st.markdown("• ✅ **Keep Current Routine**: Your patterns are healthy!")


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


def render_onboarding():
    """Render multi-step personalized onboarding with mobile optimization."""
    
    step = st.session_state.onboarding_step
    
    # Common mobile-optimized styles with enhanced animations
    st.markdown("""
    <style>
        /* Hide sidebar during onboarding */
        [data-testid="stSidebar"] { display: none; }
        
        /* Mobile-first responsive */
        .main .block-container {
            max-width: 420px !important;
            padding: 16px !important;
            margin: 0 auto;
        }
        
        /* Animated gradient background */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 20%, rgba(16, 185, 129, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
            animation: bgShift 10s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }
        
        @keyframes bgShift {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }
        
        /* Progress bar - pill style */
        .progress-bar {
            display: flex;
            gap: 6px;
            justify-content: center;
            margin-bottom: 24px;
        }
        .progress-dot {
            width: 24px;
            height: 6px;
            border-radius: 3px;
            background: rgba(255,255,255,0.15);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .progress-dot.active {
            width: 40px;
            background: linear-gradient(90deg, #10b981, #3b82f6);
            box-shadow: 0 0 12px rgba(16, 185, 129, 0.6);
        }
        .progress-dot.done {
            background: #10b981;
        }
        
        /* Logo - larger with glow */
        .onboard-logo {
            font-size: 5rem;
            text-align: center;
            margin-bottom: 8px;
            animation: logoFloat 3s ease-in-out infinite;
            filter: drop-shadow(0 0 20px rgba(16, 185, 129, 0.4));
        }
        @keyframes logoFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }
        
        /* Title - gradient with animation */
        .onboard-title {
            font-size: 1.75rem;
            font-weight: 800;
            text-align: center;
            margin: 12px 0;
            background: linear-gradient(135deg, #10b981 0%, #3b82f6 50%, #8b5cf6 100%);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientMove 4s ease infinite;
        }
        @keyframes gradientMove {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .onboard-subtitle {
            font-size: 1rem;
            color: #94a3b8 !important;
            text-align: center;
            margin-bottom: 24px;
            line-height: 1.6;
        }
        
        /* Feature list - card style */
        .feature-list {
            list-style: none;
            padding: 0;
            margin: 16px 0;
        }
        .feature-item {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 14px 16px;
            margin-bottom: 10px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            animation: slideIn 0.5s ease-out forwards;
            opacity: 0;
            transform: translateX(-20px);
        }
        .feature-item:nth-child(1) { animation-delay: 0.1s; }
        .feature-item:nth-child(2) { animation-delay: 0.2s; }
        .feature-item:nth-child(3) { animation-delay: 0.3s; }
        .feature-item:nth-child(4) { animation-delay: 0.4s; }
        
        @keyframes slideIn {
            to { opacity: 1; transform: translateX(0); }
        }
        
        .feature-icon {
            font-size: 1.5rem;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
        }
        .feature-text {
            font-size: 0.95rem;
            color: #e2e8f0 !important;
            font-weight: 500;
        }
        
        /* Goal buttons - 2x2 grid */
        .goal-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 16px 0;
        }
        
        /* Welcome text */
        .welcome-text {
            font-size: 1.6rem;
            font-weight: 700;
            text-align: center;
            color: #fff !important;
            margin: 16px 0;
            animation: fadeInUp 0.6s ease-out;
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .welcome-name {
            color: #10b981 !important;
            background: linear-gradient(90deg, #10b981, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Footer badge */
        .footer-badge {
            text-align: center;
            margin-top: 24px;
            font-size: 0.75rem;
            color: #64748b !important;
            opacity: 0.7;
        }
        
        /* Input field styling */
        .stTextInput > div > div > input {
            background: rgba(255,255,255,0.05) !important;
            border: 2px solid rgba(255,255,255,0.1) !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
            font-size: 1.1rem !important;
            color: #fff !important;
            text-align: center;
        }
        .stTextInput > div > div > input:focus {
            border-color: #10b981 !important;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2) !important;
        }
        .stTextInput > div > div > input::placeholder {
            color: #64748b !important;
        }
        
        /* Slider styling */
        .stSlider > div > div > div > div {
            background: linear-gradient(90deg, #3b82f6, #10b981) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Progress dots
    dots_html = ""
    for i in range(1, 5):
        if i < step:
            dots_html += '<div class="progress-dot done"></div>'
        elif i == step:
            dots_html += '<div class="progress-dot active"></div>'
        else:
            dots_html += '<div class="progress-dot"></div>'
    
    st.markdown(f'<div class="progress-bar">{dots_html}</div>', unsafe_allow_html=True)
    
    # === STEP 1: Welcome ===
    if step == 1:
        st.markdown("""
        <div class="onboard-logo">💎</div>
        <div class="onboard-title">Welcome to Equilibra</div>
        <div class="onboard-subtitle">
            Your AI-powered health companion that knows<br>when to push and when to protect.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-list">
            <div class="feature-item">
                <span class="feature-icon">🧠</span>
                <span class="feature-text">Reads your biometrics in real-time</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">🛡️</span>
                <span class="feature-text">Blocks harmful activities when you're drained</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">🔮</span>
                <span class="feature-text">Predicts burnout before it happens</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">💬</span>
                <span class="feature-text">Explains every decision in plain language</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Let's get started →", key="step1_next", use_container_width=True, type="primary"):
            st.session_state.onboarding_step = 2
            st.rerun()
    
    # === STEP 2: Name ===
    elif step == 2:
        st.markdown("""
        <div class="onboard-logo">👋</div>
        <div class="onboard-title">What's your name?</div>
        <div class="onboard-subtitle">
            Let's make this personal.
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("Your name", placeholder="Enter your name...", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", key="step2_back", use_container_width=True):
                st.session_state.onboarding_step = 1
                st.rerun()
        with col2:
            if st.button("Continue →", key="step2_next", use_container_width=True, type="primary"):
                if name.strip():
                    st.session_state.user_name = name.strip()
                    st.session_state.onboarding_step = 3
                    st.rerun()
                else:
                    st.warning("Please enter your name")
    
    # === STEP 3: Age & Goal ===
    elif step == 3:
        st.markdown(f"""
        <div class="onboard-logo">🎯</div>
        <div class="onboard-title">Nice to meet you, {st.session_state.user_name}!</div>
        <div class="onboard-subtitle">
            Tell us a bit about yourself.
        </div>
        """, unsafe_allow_html=True)
        
        age = st.slider("How old are you?", 16, 80, st.session_state.user_age)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**What's your main health goal?**")
        
        goals = {
            "🏃 Get Fit": "fitness",
            "😴 Sleep Better": "sleep",
            "🧘 Reduce Stress": "stress",
            "⚡ More Energy": "energy"
        }
        
        goal_cols = st.columns(2)
        selected_goal = st.session_state.user_goal
        
        for idx, (label, value) in enumerate(goals.items()):
            with goal_cols[idx % 2]:
                if st.button(label, key=f"goal_{value}", use_container_width=True, 
                           type="primary" if selected_goal == value else "secondary"):
                    st.session_state.user_goal = value
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", key="step3_back", use_container_width=True):
                st.session_state.onboarding_step = 2
                st.rerun()
        with col2:
            if st.button("Continue →", key="step3_next", use_container_width=True, type="primary"):
                if st.session_state.user_goal:
                    st.session_state.user_age = age
                    st.session_state.onboarding_step = 4
                    st.rerun()
                else:
                    st.warning("Please select a goal")
    
    # === STEP 4: Ready! ===
    elif step == 4:
        goal_emojis = {"fitness": "🏃", "sleep": "😴", "stress": "🧘", "energy": "⚡"}
        goal_emoji = goal_emojis.get(st.session_state.user_goal, "🎯")
        
        st.markdown(f"""
        <div class="onboard-logo">🎉</div>
        <div class="welcome-text">
            You're all set, <span class="welcome-name">{st.session_state.user_name}</span>!
        </div>
        <div class="onboard-subtitle">
            Equilibra is now personalized for you.<br>
            Let's start optimizing your health {goal_emoji}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-list">
            <div class="feature-item">
                <span class="feature-icon">✅</span>
                <span class="feature-text">Your profile is ready</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">�</span>
                <span class="feature-text">AI calibrated to your goals</span>
            </div>
            <div class="feature-item">
                <span class="feature-icon">�</span>
                <span class="feature-text">Circuit Breaker protection enabled</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ Enter Equilibra", key="step4_finish", use_container_width=True, type="primary"):
            # Mark onboarding as complete and save to cookie
            st.session_state.onboarding_complete = True
            persist_session_data()  # Save to browser cookie
            st.rerun()
        
        st.markdown('<div class="footer-badge">🏆 Built for HYD-300 Hackathon</div>', unsafe_allow_html=True)



def check_crisis_mode():
    """Check for burnout risk and activate crisis mode if needed."""
    if not st.session_state.get("decision_history") or len(st.session_state.decision_history) == 0:
        st.session_state.crisis_mode = False
        st.session_state.burnout_forecast = None
        return
    
    # Run burnout analysis
    forecast = st.session_state.burnout_predictor.analyze(st.session_state.decision_history)
    st.session_state.burnout_forecast = forecast
    
    # Activate crisis mode if risk is high
    if forecast.risk_score >= BurnoutPredictor.CRITICAL_THRESHOLD:
        st.session_state.crisis_mode = True
    else:
        st.session_state.crisis_mode = False


def render_crisis_banner():
    """Render crisis mode banner if active."""
    if not st.session_state.crisis_mode or not st.session_state.burnout_forecast:
        return
    
    forecast = st.session_state.burnout_forecast
    
    # Crisis banner
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        border: 2px solid #ef4444;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
    ">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 2rem;">⚠️</span>
            <div style="flex: 1;">
                <div style="font-size: 1.1rem; font-weight: 700; color: white; margin-bottom: 4px;">
                    CRISIS MODE ACTIVE
                </div>
                <div style="font-size: 0.9rem; color: rgba(255,255,255,0.9);">
                    Burnout predicted in {forecast.days_to_crisis or "?"} days based on: {", ".join(forecast.primary_factors[:2])}
                </div>
            </div>
            <div style="text-align: center; background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 8px;">
                <div style="font-size: 0.7rem; color: rgba(255,255,255,0.8);">RISK LEVEL</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: white;">{forecast.risk_score}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Emergency protocol message
    st.info("🛡️ **Emergency Protocol Engaged**: High-intensity activities have been automatically disabled. Focus on recovery today.")


def render_home():
    """Render the Home Dashboard tab."""
    st.markdown(f"### 👋 Welcome back, {st.session_state.user_name}")
    
    st.markdown("Here's your daily balance snapshot.")
    
    # 1. Key Metrics Row
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Streak Card
        streak = st.session_state.get("streak_count", 0)
        st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 12px; padding: 16px;">
            <div style="font-size: 0.8rem; color: #f59e0b; font-weight: 600;">CURRENT STREAK</div>
            <div style="font-size: 2rem; font-weight: 700;">{streak} <span style="font-size: 1rem;">days</span></div>
            <div style="font-size: 0.8rem; opacity: 0.7;">Keep it up! 🔥</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        # Adherence Card
        score = st.session_state.get("adherence_score", 85)
        color = "#10b981" if score >= 80 else "#ef4444"
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 16px;">
            <div style="font-size: 0.8rem; color: #10b981; font-weight: 600;">ADHERENCE</div>
            <div style="font-size: 2rem; font-weight: 700;">{score}<span style="font-size: 1rem;">%</span></div>
            <div style="font-size: 0.8rem; opacity: 0.7; color: {color};">On track 🎯</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        # Readiness Card (Mock derivation)
        readiness = 85
        if st.session_state.get("orchestrator") and hasattr(st.session_state.orchestrator, 'current_state') and st.session_state.orchestrator.current_state:
             s = st.session_state.orchestrator.current_state
             # Mock calc: (energy * 10 + sleep_quality) / 2
             readiness = (s.energy_level * 10 + s.sleep_quality) / 2
        
        st.markdown(f"""
        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 12px; padding: 16px;">
            <div style="font-size: 0.8rem; color: #3b82f6; font-weight: 600;">READINESS</div>
            <div style="font-size: 2rem; font-weight: 700;">{int(readiness)}<span style="font-size: 1rem;">/100</span></div>
            <div style="font-size: 0.8rem; opacity: 0.7;">System ready 🚀</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 2. Burnout Risk Meter
    if st.session_state.burnout_forecast:
        forecast = st.session_state.burnout_forecast
        risk = forecast.risk_score
        
        # Color based on severity
        if risk >= 70:
            color = "#dc2626"
            bg_color = "rgba(220, 38, 38, 0.1)"
            border_color = "rgba(220, 38, 38, 0.3)"
            status = "CRITICAL"
        elif risk >= 50:
            color = "#f59e0b"
            bg_color = "rgba(245, 158, 11, 0.1)"
            border_color = "rgba(245, 158, 11, 0.3)"
            status = "HIGH"
        elif risk >= 30:
            color = "#eab308"
            bg_color = "rgba(234, 179, 8, 0.1)"
            border_color = "rgba(234, 179, 8, 0.3)"
            status = "MODERATE"
        else:
            color = "#10b981"
            bg_color = "rgba(16, 185, 129, 0.1)"
            border_color = "rgba(16, 185, 129, 0.3)"
            status = "LOW"
        
        st.markdown("#### 🎯 Burnout Risk Monitor")
        
        st.markdown(f"""
        <div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 12px; padding: 20px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 0.8rem; color: {color}; font-weight: 600; margin-bottom: 4px;">{status} RISK</div>
                    <div style="font-size: 2.5rem; font-weight: 700; color: {color};">{risk}<span style="font-size: 1.2rem;">/100</span></div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 0.75rem; opacity: 0.7;">Primary Factor</div>
                    <div style="font-size: 0.85rem; font-weight: 500;">{forecast.primary_factors[0] if forecast.primary_factors else "None"}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 3. Daily Insight
    st.markdown("#### 💡 Today's Focus")
    st.info(f"Goal: **{st.session_state.user_goal}**. Remember, small consistent actions compound over time. Check your Decision tab to stay aligned!")
    
    # 3. Recent Activity (Mini)
    if st.session_state.decision_history:
        last = st.session_state.decision_history[-1]
        st.markdown("#### 🕒 Last Decision")
        st.markdown(f"**{last.timestamp.strftime('%H:%M')}**: {last.reasoning_summary}")
    else:
        st.markdown("#### 🚀 Get Started")
        st.markdown("No decisions logged yet today. Head to the **Make Decision** tab!")

def render_council_view():
    """Render the Council View - Multi-Agent Deliberation & Temporal Insights."""
    st.markdown("### 🤝 Health Council - Multi-Agent Deliberation")
    st.markdown("See how 4 specialized agents collaborate to make decisions")
    
    if not st.session_state.decision_history or len(st.session_state.decision_history) < 1:
        st.info("📊 Make your first decision to see the Health Council in action!")
        return
    
    # Get current state from sidebar or last decision
    current_state = {}
    if st.session_state.orchestrator and st.session_state.orchestrator.current_state:
        state = st.session_state.orchestrator.current_state
        current_state = {
            'sleep_hours': state.sleep_hours,
            'energy_level': state.energy_level,
            'stress_level': state.stress_level.value if hasattr(state.stress_level, 'value') else state.stress_level
        }
    elif st.session_state.decision_history:
        current_state = st.session_state.decision_history[-1].state_snapshot
    
    # Run Council Deliberation
    consensus = st.session_state.health_council.deliberate(
        state_snapshot=current_state,
        planned_activity="HIIT Workout",
        user_goal=st.session_state.user_goal,
        decision_history=st.session_state.decision_history
    )
    
    # Display Consensus
    st.markdown("#### 🎯 Council Decision")
    consensus_color = "#10b981" if consensus.consensus_level >= 0.75 else "#f59e0b" if consensus.consensus_level >= 0.5 else "#ef4444"
    
    st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid {consensus_color}; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 0.8rem; opacity: 0.7;">FINAL DECISION</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {consensus_color};">{consensus.final_action}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.8rem; opacity: 0.7;">CONSENSUS</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {consensus_color};">{consensus.consensus_level:.0%}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Agent Votes
    st.markdown("#### 🗳️ Agent Votes")
    cols = st.columns(4)
    
    agent_icons = {"sleep": "😴", "performance": "⚡", "wellness": "🧘", "future": "🔮"}
    
    for idx, vote in enumerate(consensus.agent_votes):
        with cols[idx]:
            icon = agent_icons.get(vote.agent_role.value, "🤖")
            action_color = "#10b981" if vote.action == "PROCEED" else "#f59e0b" if vote.action == "MODIFY" else "#ef4444"
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                <div style="font-size: 1.5rem; text-align: center;">{icon}</div>
                <div style="font-size: 0.7rem; text-align: center; text-transform: uppercase; opacity: 0.7;">{vote.agent_role.value}</div>
                <div style="font-size: 0.9rem; text-align: center; font-weight: 600; color: {action_color}; margin-top: 4px;">{vote.action}</div>
                <div style="font-size: 0.65rem; text-align: center; opacity: 0.6; margin-top: 4px;">Confidence: {vote.confidence:.0%}</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Reasoning"):
                st.markdown(f"_{vote.reasoning}_")
    
    # Dissenting Opinions
    if consensus.dissenting_opinions:
        st.markdown("#### ⚠️ Dissenting Opinions")
        for opinion in consensus.dissenting_opinions:
            st.warning(opinion)
    
    st.markdown("---")
    
    # Temporal Insights
    st.markdown("### ⏰ Temporal Analysis")
    
    temporal = st.session_state.temporal_reasoner.analyze_timeline(
        decision_history=st.session_state.decision_history,
        current_state=current_state
    )
    
    # Urgency Badge
    urgency_colors = {1: "#10b981", 2: "#3b82f6", 3: "#f59e0b", 4: "#ef4444", 5: "#dc2626"}
    urgency_labels = {1: "LOW", 2: "MODERATE", 3: "ELEVATED", 4: "HIGH", 5: "CRITICAL"}
    
    st.markdown(f"""
    <div style="background: {urgency_colors[temporal.urgency_level]}; color: white; padding: 8px 16px; border-radius: 8px; display: inline-block; font-weight: 600; margin-bottom: 16px;">
        URGENCY: {urgency_labels[temporal.urgency_level]}
    </div>
    """, unsafe_allow_html=True)
    
    # Recommendation
    st.info(f"**Recommendation**: {temporal.recommendation}")
    
    # Past Patterns
    if temporal.past_patterns:
        st.markdown("#### 📊 Detected Patterns")
        for pattern in temporal.past_patterns:
            st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b; padding: 12px; margin-bottom: 8px;">
                <div style="font-weight: 600;">{pattern.description}</div>
                <div style="font-size: 0.85rem; opacity: 0.8;">Frequency: {pattern.frequency:.0%} | Confidence: {pattern.confidence:.0%}</div>
                <div style="font-size: 0.8rem; opacity: 0.7; margin-top: 4px;">{pattern.examples[0] if pattern.examples else ""}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Present Context
    st.markdown("#### 🎯 Present Context")
    st.markdown(f"**Day**: {temporal.present_context.day_of_week} | **Time**: {temporal.present_context.time_of_day}")
    st.markdown(f"**Risk Level**: {temporal.present_context.risk_level.upper()}")
    
    if temporal.present_context.risk_factors:
        st.markdown("**Risk Factors**:")
        for factor in temporal.present_context.risk_factors:
            st.markdown(f"• {factor}")
    
    # Future Trajectories
    if temporal.future_trajectories:
        st.markdown("#### 🔮 Future Projections")
        for traj in temporal.future_trajectories:
            impact_colors = {"minor": "#10b981", "moderate": "#f59e0b", "major": "#ef4444", "severe": "#dc2626"}
            
            st.markdown(f"""
            <div style="background: rgba(220, 38, 38, 0.1); border: 1px solid {impact_colors.get(traj.impact_level, '#888')}; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                <div style="font-weight: 600;">{traj.timeline}: {traj.predicted_outcome}</div>
                <div style="font-size: 0.85rem; opacity: 0.8;">Probability: {traj.probability:.0%} | Impact: {traj.impact_level.upper()}</div>
                {f'<div style="font-size: 0.8rem; color: #10b981; margin-top: 4px;">⏰ Intervention Window: {traj.intervention_window}</div>' if traj.intervention_window else ''}
            </div>
            """, unsafe_allow_html=True)

# Main app
def main():
    # Show onboarding for first-time users
    if not st.session_state.onboarding_complete:
        render_onboarding()
        return
    
    # Get sidebar inputs
    inputs = render_sidebar()
    
    # Check for crisis mode
    check_crisis_mode()
    
    # Render header with settings
    render_header()
    
    # Show crisis banner if active
    render_crisis_banner()
    
    # Render friendly scenario picker
    render_feeling_picker()
    
    # Tab navigation
    tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏠 Home",
        "🤝 Council",
        "🎯 Make Decision",
        "📅 Simulation", 
        "💬 Chat",
        "📈 History",
        "🔄 Adaptation",
        "ℹ️ About"
    ])
    
    with tab0:
        render_home()
        
    with tab1:
        render_council_view()
        
    with tab2:
        render_make_decision(inputs)
    
    with tab3:
        render_simulation()
    
    with tab4:
        render_chat()
    
    with tab5:
        render_history()
    
    with tab6:
        render_adaptation()
    
    with tab7:
        render_about()


if __name__ == "__main__":
    main()
