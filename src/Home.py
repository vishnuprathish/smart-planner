import streamlit as st
from pathlib import Path
from services.openai_service import OpenAIService
from services.firebase_service import FirebaseService
from services.pdf_service import PDFService
from components.welcome import show_welcome_section
from components.ui import get_pdf_download_link
from utils.session import init_session_state, is_valid_email
from test_data import get_test_goal
import base64
import sys

# Helper functions
def all_questions_answered():
    if not st.session_state.questions:
        return False
    return all(st.session_state.get(f"answer_{i}") for i in range(len(st.session_state.questions)))

def show_reminder_form():
    st.session_state.show_reminder_form = True

def reset_form():
    st.session_state.questions = None
    st.session_state.show_questions = False
    st.session_state.current_plan = None
    st.session_state.show_reminder_form = False
    st.session_state.plan_saved = False

def check_connectivity():
    """Check if we can connect to OpenAI's API."""
    try:
        import socket
        socket.create_connection(("api.openai.com", 443), timeout=5)
        return True
    except OSError:
        return False

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
    st.session_state.current_plan = None
    st.session_state.plan_saved = False
    st.session_state.user_email = None

init_session_state()

# Check if test mode is enabled via command line
TEST_MODE_ENABLED = "--test-mode" in sys.argv

# Initialize test mode defaults if enabled
if TEST_MODE_ENABLED and 'test_mode' not in st.session_state:
    st.session_state.test_mode = True
    st.session_state.test_goal_type = "Fitness"
    test_data = get_test_goal('fitness')
    if test_data:
        st.session_state.goal_input = test_data['goal']

# Load CSS
css_path = Path(__file__).parent / "styles" / "main.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize services
try:
    openai_service = OpenAIService()  # No need to pass api_key, it will use st.secrets
    firebase_service = FirebaseService()
    pdf_service = PDFService()
except Exception as e:
    st.error(f"Error initializing services: {str(e)}")
    st.stop()

# Check connectivity before proceeding
if not check_connectivity():
    st.error("""
        ⚠️ Unable to connect to the internet. Please:
        1. Check your internet connection
        2. Refresh the page
        3. Try again in a few moments
        
        If the problem persists, your network might be blocking the connection.
    """)
    st.stop()

# Show welcome section
show_welcome_section()

# Add test mode in sidebar only if enabled
if TEST_MODE_ENABLED:
    with st.sidebar:
        st.markdown("### 🧪 Test Mode")
        test_mode = st.checkbox("Enable Test Mode", key="test_mode")
        
        if test_mode:
            test_goal_type = st.selectbox(
                "Select a test goal",
                ["Fitness", "Career", "Finance"],
                key="test_goal_type"
            )
            
            if st.button("Load Test Data"):
                test_data = get_test_goal(test_goal_type.lower())
                if test_data:
                    # Set the goal
                    st.session_state.goal_input = test_data['goal']
                    
                    # Set up questions and answers
                    questions = [
                        "What's motivating you to achieve this goal?",
                        "What obstacles might you face?",
                        "What resources do you have available?",
                        "How will you track your progress?",
                        "What's your current situation regarding this goal?"
                    ]
                    answers = list(test_data['answers'].values())
                    
                    # Store questions in session state
                    st.session_state.questions = questions
                    
                    # Store answers with proper keys
                    for i, answer in enumerate(answers):
                        st.session_state[f"answer_{i}"] = answer
                    
                    st.session_state.show_questions = True
                    st.rerun()

# Streamlit app layout
if not st.session_state.current_plan:
    st.session_state.current_step = 1
    
    # Goal input section
    st.markdown("<div class='info-box' style='margin-top: 0.5em;'>", unsafe_allow_html=True)
    st.markdown("### What's your goal? 🎯")
    st.markdown("""
        <div class='tip-box' style='margin: 0.5em 0;'>
            <strong>Pro Tip:</strong> Be specific! Instead of "get fit", try "run a 5K in under 30 minutes by March 2024"
        </div>
    """, unsafe_allow_html=True)
    
    goal = st.text_input("", key="goal_input", placeholder="Enter your goal here...", 
                        help="Be specific, measurable, and time-bound")
    
   
    
    
    # Email collection with clear benefits
    st.markdown("""
        <div style='text-align: center; margin: 1em 0;'>
            <p style='color: #444; font-size: 1.1em; font-weight: 500;'>
                📧 Optionally, enter your email to receive reminders for your daily micro-habits
            </p>
        </div>
    """, unsafe_allow_html=True)

    email = st.text_input(
        "",
        placeholder="Enter your email (optional)",
        key="email_input"
    )
        
    if email and not is_valid_email(email):
        st.error("Oops! That email doesn't look quite right. Mind double-checking? 🤔")

    if st.button("Begin My Journey", key="start_button", type="primary"):
        if not goal:
            st.warning("🎯 Please enter your goal first!")
        else:
            # Store email in session state if provided
            if email:
                st.session_state.user_email = email
            with st.spinner("🤔 Analyzing your goal..."):
                st.session_state.questions = openai_service.generate_questions(goal)
                st.session_state.show_questions = True

# Display questions and collect answers
if st.session_state.show_questions and st.session_state.questions and not st.session_state.current_plan:
    st.session_state.current_step = 2
    
    st.markdown("""
        <div style='text-align: center; margin: 2em 0;'>
            <span class='step-counter'>STEP 2</span>
            <span style='font-size: 1.2em; font-weight: 500;'>Let's understand your goal better</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class='tip-box'>
            <strong>Pro Tip:</strong> The more detailed your answers, the better we can customize your plan. Think about your specific challenges and preferences.
        </div>
    """, unsafe_allow_html=True)
    
    # Questions in two columns
    questions = st.session_state.questions
    mid_point = len(questions) // 2
    
    col1, col2 = st.columns(2)
    with col1:
        for i in range(mid_point):
            st.text_input(
                questions[i],
                key=f"answer_{i}",
                placeholder="Your answer here..."
            )
    with col2:
        for i in range(mid_point, len(questions)):
            st.text_input(
                questions[i],
                key=f"answer_{i}",
                placeholder="Your answer here..."
            )

    st.markdown("""
        <div style='text-align: center; margin: 2em 0;'>
            <p style='color: #666; font-size: 1.1em;'>Now, let's make sure your plan fits your schedule:</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        time_commitment = st.slider(
            "Daily time commitment:",
            min_value=5,
            max_value=180,
            value=30,
            step=5,
            help="Slide to select your daily time commitment"
        )
        st.markdown(f"<p style='text-align: center;'>I can commit <span class='highlight-text'>{time_commitment} minutes</span> per day</p>", unsafe_allow_html=True)

    st.markdown("""
        <div class='tip-box'>
            <strong>Pro Tip:</strong> Be realistic with your time commitment. It's better to start small and build up than to overcommit and get discouraged.
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='big-button'>", unsafe_allow_html=True)
        if st.button("Create My Success Plan", type="primary"):
            if not all_questions_answered():
                st.error("🤔 Please answer all questions first!")
                st.stop()
            if time_commitment <= 0:
                st.error("⏰ Please set your daily time commitment!")
                st.stop()

            with st.spinner("🎨 Creating your personalized plan..."):
                goal = st.session_state.goal_input
                questions = st.session_state.questions
                answers = [st.session_state[f"answer_{i}"] for i in range(len(questions))]
                
                # Generate the plan
                plan = openai_service.generate_plan(goal, questions, answers)
                
                if plan:
                    st.session_state.current_plan = plan
                    st.session_state.plan_saved = False
                    st.rerun()
                else:
                    st.error("Failed to generate plan. Please try again.")
        st.markdown("</div>", unsafe_allow_html=True)

# Display plan and reminder option
if st.session_state.current_plan and not st.session_state.plan_saved:
    st.session_state.current_step = 3
    
    # Add custom CSS for responsiveness
    st.markdown("""
        <style>
            @media (max-width: 768px) {
                .strategy-box {
                    padding: 0 !important;
                }
                .initiative-card {
                    margin: 0.8em 0 !important;
                }
                .initiative-title {
                    font-size: 0.9em !important;
                }
                .initiative-desc {
                    font-size: 0.85em !important;
                }
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class='strategy-box'>
            <h3 style='color: #FF4B4B; margin-bottom: 1em; text-align: center; font-size: min(1.8em, 7vw);'>🎯 Strategic Initiatives</h3>
            <div style='background: #2D2D2D; padding: min(1.2em, 4vw); border-radius: 10px; margin-bottom: 1em;'>
    """, unsafe_allow_html=True)
    
    # Display each strategic initiative
    initiatives = [point for point in st.session_state.current_plan['initiatives'].split('\n') if point.strip()]
    for i, initiative in enumerate(initiatives, 1):
        parts = initiative.split(':', 1)
        if len(parts) == 2:
            title, description = parts
            st.markdown(f"""
                <div class='initiative-card' style='margin-bottom: 1.5em; background: #383838; padding: min(1.2em, 4vw); border-radius: 10px; border-left: 4px solid #FF4B4B;'>
                    <div style='display: flex; align-items: flex-start; gap: min(12px, 3vw);'>
                        <div style='background: #FF4B4B; color: white; border-radius: 50%; min-width: 28px; height: 28px; 
                                display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: bold;'>
                            {i}
                        </div>
                        <div style='flex: 1;'>
                            <div class='initiative-title' style='color: #FF4B4B; font-weight: 600; font-size: min(1.1em, 4.5vw); margin-bottom: 0.5em;'>{title}</div>
                            <div class='initiative-desc' style='color: #E0E0E0; line-height: 1.5; font-size: min(1em, 4vw);'>{description}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='initiative-card' style='margin-bottom: 1.5em; background: #383838; padding: min(1.2em, 4vw); border-radius: 10px; border-left: 4px solid #FF4B4B;'>
                    <div style='display: flex; align-items: flex-start; gap: min(12px, 3vw);'>
                        <div style='background: #FF4B4B; color: white; border-radius: 50%; min-width: 28px; height: 28px; 
                                display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: bold;'>
                            {i}
                        </div>
                        <div class='initiative-desc' style='flex: 1; color: #E0E0E0; line-height: 1.5; font-size: min(1em, 4vw);'>{initiative}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display micro-habits
    st.markdown("""
        <h3 style='color: #FF4B4B; margin: 1.5em 0 1em; text-align: center; font-size: min(1.8em, 7vw);'>✨ Daily Micro-habits</h3>
        <div style='background: #2D2D2D; padding: min(1.2em, 4vw); border-radius: 10px;'>
    """, unsafe_allow_html=True)
    
    micro_habits = [habit for habit in st.session_state.current_plan['habits'].split('\n') if habit.strip()]
    for i, habit in enumerate(micro_habits, 1):
        st.markdown(f"""
            <div style='display: flex; align-items: flex-start; margin-bottom: 1em; background: #383838; padding: min(1em, 4vw); border-radius: 10px; gap: min(12px, 3vw);'>
                <div style='background: #FF4B4B; color: white; border-radius: 50%; min-width: 28px; height: 28px; 
                           display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: bold;'>
                    {i}
                </div>
                <div style='flex: 1; color: #E0E0E0; line-height: 1.5; font-size: min(1em, 4vw);'>{habit}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add PDF download button with responsive styling
    st.markdown("""
        <div style='text-align: center; margin-top: min(2em, 6vw);'>
            <style>
                .download-button {
                    background-color: #FF4B4B;
                    color: white;
                    padding: 1em 2em;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    display: inline-block;
                    transition: background-color 0.3s;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .download-button:hover {
                    background-color: #E43E3E;
                }
                @media (max-width: 768px) {
                    .download-button {
                        width: 100% !important;
                        padding: 0.8em !important;
                        font-size: 0.9em !important;
                    }
                }
            </style>
        </div>
    """, unsafe_allow_html=True)
    
    pdf_path = pdf_service.create_pdf(
        st.session_state.current_plan['goal'],
        initiatives,
        micro_habits
    )
    st.markdown(
        get_pdf_download_link(pdf_path, "📥 Download Your Strategic Plan"),
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Email reminder section
    if not st.session_state.user_email:
        st.markdown("""
            <div style='text-align: center; margin: 2em 0 1em;'>
                <p style='color: #666; font-size: 1em;'>
                    Want daily reminders? Add your email below.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input(
            "",
            placeholder="Enter your email (optional)",
            key="email_reminder"
        )
        
        if email and not is_valid_email(email):
            st.error("Please enter a valid email address")
            email = None
    else:
        email = st.session_state.user_email
    
    # Save button
    st.markdown("<div style='margin-top: min(2em, 6vw);'>", unsafe_allow_html=True)
    if st.button("Save My Plan", type="primary"):
        if email:
            st.session_state.user_email = email
        
        try:
            # Save to Firebase
            firebase_service.store_user_goal(
                goal=st.session_state.current_plan['goal'],
                questions=st.session_state.current_plan['questions'],
                answers=st.session_state.current_plan['answers'],
                time_commitment=st.session_state.current_plan['time_commitment'],
                initiatives=st.session_state.current_plan['initiatives'],
                habits=st.session_state.current_plan['habits'],
                reminder_settings={
                    'email': st.session_state.user_email,
                    'frequency': 'Daily',
                    'time': None,
                    'status': 'active'
                }
            )
            st.session_state.plan_saved = True
            st.success("✨ Your plan has been saved!")
        except Exception as e:
            st.error(f"Error saving plan: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.plan_saved:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='big-button'>", unsafe_allow_html=True)
        if st.button("Create Another Goal"):
            reset_form()
        st.markdown("</div>", unsafe_allow_html=True)

# Add a note about the admin dashboard
with st.sidebar:
    st.info("👉 Check the Admin Dashboard to view all goals and analytics.")
