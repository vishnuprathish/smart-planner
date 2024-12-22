import streamlit as st

def show_welcome_section():
    """Display the welcome section with title and description."""
    st.markdown("""
        <div style="text-align: center; padding: 2em 0;">
            <h1 style="
                color: #FF4B4B;
                font-size: 2.5em;
                margin-bottom: 0.5em;
            ">
                🎯 Smart Goal Planner
            </h1>
        </div>
    """, unsafe_allow_html=True)
