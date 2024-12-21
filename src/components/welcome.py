import streamlit as st

def show_welcome_section():
    """Display the welcome section with title and description."""
    st.markdown("""
        <div style='margin: 1em auto; max-width: 90%; padding: 0 1em;'>
            <h1 style='text-align: center; margin-bottom: 0.5em;'>
                🎯 Smart Goal Planner
                <br>
                <span style='font-size: 0.6em; font-weight: normal; color: #666;'>
                    Turn Your Dreams into Reality with AI-Powered Goal Achievement
                </span>
            </h1>
        </div>
    """, unsafe_allow_html=True)
