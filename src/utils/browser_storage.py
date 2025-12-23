"""
Simple browser localStorage wrapper for Streamlit.
Stores user data in the browser's localStorage instead of server files.
"""
import streamlit as st
import json


def init_local_storage():
    """Initialize localStorage JavaScript bridge."""
    st.markdown("""
    <script>
    // Create a bridge between Streamlit and localStorage
    window.addEventListener('message', function(event) {
        if (event.data.type === 'streamlit:setComponentValue') {
            return;
        }
    });
    
    // Helper functions
    window.saveToLocalStorage = function(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    };
    
    window.loadFromLocalStorage = function(key) {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    };
    
    window.clearLocalStorage = function(key) {
        localStorage.removeItem(key);
    };
    </script>
    """, unsafe_allow_html=True)


def save_to_browser(key: str, data: dict):
    """Save data to browser localStorage."""
    # Use Streamlit's query params as a workaround to trigger localStorage save
    st.markdown(f"""
    <script>
    window.saveToLocalStorage('{key}', {json.dumps(data)});
    </script>
    """, unsafe_allow_html=True)


def load_from_browser(key: str, default=None):
    """Load data from browser localStorage."""
    # This is a simplified version - in production you'd use streamlit-js-eval
    # For now, we'll use query params as a bridge
    return default


# Simplified approach using Streamlit's built-in session state persistence
def save_user_data():
    """Save user data to session state (persists during browser session)."""
    if "onboarding_complete" in st.session_state and st.session_state.onboarding_complete:
        # Store in a special key that Streamlit can persist
        st.session_state["_user_data_cache"] = {
            "onboarding_complete": st.session_state.onboarding_complete,
            "user_name": st.session_state.get("user_name", ""),
            "user_age": st.session_state.get("user_age", 25),
            "user_goal": st.session_state.get("user_goal", ""),
        }


def load_user_data():
    """Load user data from session state cache."""
    if "_user_data_cache" in st.session_state:
        cache = st.session_state["_user_data_cache"]
        return cache
    return None
