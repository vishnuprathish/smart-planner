import streamlit as st

def show_welcome_section():
    """Display the welcome section with title and description."""
    st.markdown("""
        <div style='margin: 2em 180px 2em 2em;'>
            <h1 style='text-align: center; margin-bottom: 1em;'>
                🎯 Smart Goal Planner
                <br>
                <span style='font-size: 0.6em; font-weight: normal; color: #666;'>
                    Turn Your Dreams into Reality with AI-Powered Goal Achievement
                </span>
            </h1>
            <div style='text-align: center; margin-bottom: 2em;'>
                <p style='color: #555; font-size: 1.1em; max-width: 600px; margin: 0 auto;'>
                    Join thousands who've achieved their goals using our proven system. 
                    We combine AI-driven insights with psychology-backed strategies to create 
                    your personalized success roadmap. 🚀
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
