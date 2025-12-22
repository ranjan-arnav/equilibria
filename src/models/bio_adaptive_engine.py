
"""
Bio-Adaptive Engine (The Chameleon)
Logic for morphing the UI based on biometric state.
"""
from enum import Enum
from src.models.health_state import HealthState, StressLevel, EnergyLevel

class UIMode(Enum):
    BALANCED = "Balanced"
    ZEN = "Zen Mode"
    HUNTER = "Hunter Mode"

class BioAdaptiveEngine:
    """
    Determines the optimal UI mode and returns the corresponding CSS.
    """
    
    @staticmethod
    def determine_mode(state: HealthState) -> UIMode:
        """
        Map health state to UI mode.
        - High Stress -> ZEN (Calm, minimal)
        - High Energy + Low Stress -> HUNTER (Aggressive, detailed)
        - Otherwise -> BALANCED
        """
        if state.stress_level == StressLevel.HIGH:
            return UIMode.ZEN
        elif state.stress_level == StressLevel.MEDIUM and state.energy_level <= 3:
            return UIMode.ZEN
        elif state.stress_level == StressLevel.LOW and state.energy_level >= 7:
            return UIMode.HUNTER
        else:
            return UIMode.BALANCED

    @staticmethod
    def get_theme_css(mode: UIMode) -> str:
        """Returns the specific CSS injection for the mode."""
        
        base_css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Outfit:wght@500;700&display=swap');
        * { transition: all 0.5s ease-in-out; }
        """
        
        if mode == UIMode.ZEN:
            return base_css + """
            /* ZEN MODE: Sage Green, Rounded, Minimal */
            .stApp {
                background: linear-gradient(180deg, #2C3E50 0%, #4B79A1 100%) !important; 
                /* Fallback to a softer dark blue/slate if the gradient is too much, 
                   but let's go for a 'Forest at Night' vibe */
                background: linear-gradient(180deg, #1a2a1a 0%, #2f4f4f 100%) !important;
            }
            h1, h2, h3, p, div {
                font-family: 'Inter', sans-serif !important;
                color: #A8D5BA !important; /* Sage text */
            }
            .stButton>button {
                border-radius: 50px !important;
                background-color: rgba(168, 213, 186, 0.2) !important;
                border: 1px solid #A8D5BA !important;
                color: #A8D5BA !important;
            }
            /* Hide complex elements in Zen Mode */
            .hunter-only { display: none !important; }
            .metric-container { opacity: 0.7; }
            </style>
            """
            
        elif mode == UIMode.HUNTER:
            return base_css + """
            /* HUNTER MODE: High Contrast, Sharp, Neon */
            .stApp {
                background: #000000 !important;
            }
            h1, h2, h3, div {
                font-family: 'Outfit', sans-serif !important;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            h1 {
                text-shadow: 0 0 10px #FF4500;
                color: #FF4500 !important; /* Neon Orange */
            }
            h3, p, label {
                 color: #00FFFF !important; /* Cyan accents */
            }
            .stButton>button {
                border-radius: 0px !important; /* Sharp edges */
                background: #FF4500 !important;
                color: black !important;
                font-weight: bold !important;
                box-shadow: 4px 4px 0px #00FFFF;
                border: none !important;
            }
            /* Hide Zen elements */
            .zen-only { display: none !important; }
            </style>
            """
            
        else: # BALANCED
            return base_css + """
            /* BALANCED: Professional Dark Blue */
            .stApp {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            }
            h1, h2, h3 { color: #ffffff !important; font-family: 'Inter', sans-serif; }
            p { color: #cbd5e1 !important; }
            .stButton>button {
                border-radius: 8px !important;
                background: #3b82f6 !important;
                color: white !important;
            }
            </style>
            """
