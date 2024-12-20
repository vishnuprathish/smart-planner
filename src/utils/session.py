import streamlit as st

def init_session_state():
    """Initialize session state variables."""
    # User progress
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
        
    # Goal and plan
    if 'current_goal' not in st.session_state:
        st.session_state.current_goal = None
    if 'current_plan' not in st.session_state:
        st.session_state.current_plan = None
        
    # Questions and answers
    if 'questions' not in st.session_state:
        st.session_state.questions = None
    if 'show_questions' not in st.session_state:
        st.session_state.show_questions = False
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
        
    # Reminders and email
    if 'show_reminder_form' not in st.session_state:
        st.session_state.show_reminder_form = False
    if 'plan_saved' not in st.session_state:
        st.session_state.plan_saved = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
