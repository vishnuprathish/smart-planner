import streamlit as st

def show_progress_bar(current_step: int):
    """Display the progress bar with the current step highlighted."""
    st.markdown("""
        <div class='progress-container'>
            <div class='progress-bar-container'>
                <div class='progress-bar'>
    """, unsafe_allow_html=True)
    
    steps = [
        ("1", "Set Goal"),
        ("2", "Questions"),
        ("3", "Plan"),
        ("4", "Reminders")
    ]
    
    for i, (num, label) in enumerate(steps, 1):
        status = ""
        if i < current_step:
            status = "completed"
        elif i == current_step:
            status = "active"
        
        st.markdown(f"""
            <div class='progress-step-container'>
                <div class='progress-step {status}'>
                    {num}
                </div>
                <div class='progress-label'>{label}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
