import streamlit as st
from services.firebase_service import FirebaseService
from datetime import datetime

# Initialize Firebase service
try:
    firebase_service = FirebaseService()
except Exception as e:
    st.error(f"Error initializing Firebase: {str(e)}")
    st.stop()

# Page config
st.set_page_config(page_title="Admin Dashboard", page_icon="🔒", layout="wide")

# Password protection
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "D642v307xdvy!@#":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

if check_password():
    st.title("🔒 Admin Dashboard")
    
    # Get all goals
    goals = firebase_service.get_user_goals(limit=100)  # Increased limit for admin view
    
    # Calculate metrics
    total_goals = len(goals)
    goals_with_reminders = sum(1 for goal in goals if 'reminder_settings' in goal and goal['reminder_settings'])
    avg_time = sum(int(goal['time_commitment']) if isinstance(goal['time_commitment'], int) else int(goal['time_commitment']) for goal in goals if isinstance(goal['time_commitment'], (int, str)) and (isinstance(goal['time_commitment'], str) and goal['time_commitment'].isdigit() or isinstance(goal['time_commitment'], int))) / total_goals if total_goals > 0 else 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Goals", total_goals)
    with col2:
        st.metric("Goals with Reminders", goals_with_reminders)
    with col3:
        st.metric("Avg. Time Commitment", f"{avg_time:.0f} min")
    
    # Display all goals in a table
    st.subheader("All Goals")
    
    # Create a table view
    if goals:
        # Headers
        col1, col2, col3, col4, col5 = st.columns([3, 1, 2, 2, 2])
        with col1:
            st.write("**Goal**")
        with col2:
            st.write("**Time (min)**")
        with col3:
            st.write("**Created**")
        with col4:
            st.write("**Email**")
        with col5:
            st.write("**Reminder**")
        
        # Data rows
        for goal in goals:
            col1, col2, col3, col4, col5 = st.columns([3, 1, 2, 2, 2])
            with col1:
                st.write(goal['goal'][:50] + "..." if len(goal['goal']) > 50 else goal['goal'])
            with col2:
                st.write(goal['time_commitment'])
            with col3:
                st.write(goal['timestamp'])
            with col4:
                if 'reminder_settings' in goal and goal['reminder_settings']:
                    st.write(goal['reminder_settings']['email'])
                else:
                    st.write("-")
            with col5:
                if 'reminder_settings' in goal and goal['reminder_settings']:
                    st.write(f"{goal['reminder_settings']['frequency']} at {goal['reminder_settings']['time']}")
                else:
                    st.write("-")
            
            # Expandable details
            with st.expander("View Details"):
                st.write("**Tasks:**")
                st.write(goal['tasks'])
                st.write("**Habits:**")
                st.write(goal['habits'])
                if 'reminder_settings' in goal and goal['reminder_settings']:
                    st.write("**Reminder Settings:**")
                    st.write(f"Email: {goal['reminder_settings']['email']}")
                    st.write(f"Frequency: {goal['reminder_settings']['frequency']}")
                    st.write(f"Time: {goal['reminder_settings']['time']}")
    else:
        st.info("No goals found in the database.")
