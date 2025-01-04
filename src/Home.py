import streamlit as st
from pathlib import Path
from services.openai_service import OpenAIService
from services.firebase_service import FirebaseService
from services.pdf_service import PDFService
from services.user_service import UserService
from services.goal_refinement_service import GoalRefinementService
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
    st.session_state.initial_goal = None
    st.session_state.refined_goal = None
    st.session_state.refinement_questions = None
    st.session_state.show_refinement_response = False

def check_connectivity():
    """Check if we can connect to OpenAI's API."""
    try:
        import socket
        socket.create_connection(("api.openai.com", 443), timeout=5)
        return True
    except OSError:
        return False

def save_entries():
    try:
        # Ensure time_commitment is set
        if 'time_commitment' not in st.session_state.current_plan:
            st.session_state.current_plan['time_commitment'] = time_commitment
        # Save to Firebase
        firebase_service.store_user_goal(
            goal=st.session_state.current_plan['goal'],
            questions=st.session_state.current_plan['questions'],
            answers=st.session_state.current_plan['answers'],
            time_commitment=st.session_state.current_plan['time_commitment'],
            tasks=st.session_state.current_plan['initiatives'],  # Assuming you want to store initiatives here
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

# Initialize services
openai_service = OpenAIService()
pdf_service = PDFService()
user_service = UserService()
firebase_service = FirebaseService()
goal_refinement_service = GoalRefinementService()

# Constants
TEST_MODE_ENABLED = "--test-mode" in sys.argv

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
    st.session_state.current_plan = None
    st.session_state.initial_goal = None
    st.session_state.refined_goal = None
    st.session_state.refinement_questions = None
    st.session_state.show_refinement_response = False

init_session_state()

# Initialize test mode defaults if enabled
if TEST_MODE_ENABLED and 'test_mode' not in st.session_state:
    st.session_state.test_mode = True
    st.session_state.test_goal_type = "Fitness"
    test_data = get_test_goal('fitness')
    if test_data:
        st.session_state.initial_goal = None
        st.session_state.refinement_questions = None
        st.session_state.show_refinement_response = False
        st.session_state.refined_goal = None
        st.session_state.goal_input = None

# Load CSS
css_path = Path(__file__).parent / "styles" / "main.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
                    st.write("DEBUG - Loading test data for:", test_goal_type)  # Debug log
                    st.write("DEBUG - Test data:", test_data)  # Debug log
                    
                    # Reset all states first
                    st.session_state.initial_goal = None
                    st.session_state.refinement_questions = None
                    st.session_state.refined_goal = None
                    st.session_state.show_refinement_response = False
                    st.session_state.show_questions = False
                    st.session_state.current_plan = None
                    st.session_state.goal_input = None
                    
                    st.write("DEBUG - Reset all states")  # Debug log
                    st.rerun()

# Streamlit app layout
if not st.session_state.current_plan:
    st.session_state.current_step = 1
    
    # Goal input section
    st.markdown("<div class='info-box' style='margin-top: 0.5em;'>", unsafe_allow_html=True)
    
    # Step 1: Initial Goal Input
    initial_goal_container = st.container()
    with initial_goal_container:
        st.markdown("### Step 1: What's your goal?")
        test_data = get_test_goal(st.session_state.test_goal_type.lower()) if TEST_MODE_ENABLED and st.session_state.test_mode else None
        
        with st.form("initial_goal_form"):
            goal_input = st.text_area(
                "Enter your goal",
                value=test_data['initial_goal'] if test_data else "",
                placeholder="Example: I want to get a promotion",
                height=100
            )
            submit_goal = st.form_submit_button("Continue", type="primary")
            
            if submit_goal and goal_input.strip():
                st.session_state.initial_goal = goal_input
                questions = goal_refinement_service.get_refinement_questions(goal_input)
                if questions:
                    st.session_state.refinement_questions = questions
                    st.session_state.show_refinement_response = True
                    st.rerun()
    
    # Step 2: Refinement Questions
    if st.session_state.show_refinement_response:
        refinement_container = st.container()
        with refinement_container:
            st.markdown("### Step 2: Let's refine your goal")
            st.write(st.session_state.refinement_questions)
            
            with st.form("refinement_form"):
                refinement_response = st.text_area(
                    "Your response",
                    height=100
                )
                submit_refinement = st.form_submit_button("Continue", type="primary")
                
                if submit_refinement and refinement_response.strip():
                    refined_goal = goal_refinement_service.generate_refined_goal(
                        st.session_state.initial_goal,
                        refinement_response
                    )
                    if refined_goal:
                        st.session_state.refined_goal = refined_goal
                        st.rerun()
    
    # Step 3: Show Refined Goal
    if st.session_state.refined_goal:
        final_goal_container = st.container()
        with final_goal_container:
            st.markdown("### Step 3: Your Refined Goal")
            st.info(st.session_state.refined_goal)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Start Over", key="start_over"):
                    st.session_state.initial_goal = None
                    st.session_state.refined_goal = None
                    st.session_state.refinement_questions = None
                    st.session_state.show_refinement_response = False
                    st.rerun()
            with col2:
                if st.button("Begin My Journey", key="begin_journey", type="primary"):
                    st.session_state.goal_input = st.session_state.refined_goal
                    st.session_state.questions = openai_service.generate_questions(st.session_state.refined_goal)
                    if st.session_state.questions:
                        st.session_state.show_questions = True
                        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

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
                    placeholder="Your answer here...",
                    label_visibility="visible"
                )
        with col2:
            for i in range(mid_point, len(questions)):
                st.text_input(
                    questions[i],
                    key=f"answer_{i}",
                    placeholder="Your answer here...",
                    label_visibility="visible"
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
                    goal = st.session_state.refined_goal
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
    
    # Display the plan
    st.markdown("<h3 style='text-align: center; color: #1f1f1f;'>🎯 Your Success Plan</h3>", unsafe_allow_html=True)
    
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
                <div class='initiative-card' style='margin-bottom: 1.5em; background: #383838; padding: min(1.2em, 4vw); border-radius: 10px; gap: min(12px, 3vw);'>
                    <div style='background: #FF4B4B; color: white; border-radius: 50%; min-width: 28px; height: 28px; 
                                display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: bold;'>
                        {i}
                    </div>
                    <div style='flex: 1;'>
                        <div class='initiative-title' style='color: #FF4B4B; font-weight: 600; font-size: min(1.1em, 4.5vw); margin-bottom: 0.5em;'>{title}</div>
                        <div class='initiative-desc' style='color: #E0E0E0; line-height: 1.5; font-size: min(1em, 4vw);'>{description}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='initiative-card' style='margin-bottom: 1.5em; background: #383838; padding: min(1.2em, 4vw); border-radius: 10px; gap: min(12px, 3vw);'>
                    <div style='background: #FF4B4B; color: white; border-radius: 50%; min-width: 28px; height: 28px; 
                                display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: bold;'>
                        {i}
                    </div>
                    <div class='initiative-desc' style='flex: 1; color: #E0E0E0; line-height: 1.5; font-size: min(1em, 4vw);'>{initiative}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Display one-time actions
    st.markdown("""
        <h3 style='color: #FF4B4B; margin: 1.5em 0 1em; text-align: center; font-size: min(1.8em, 7vw);'>🔧 One-time Setup Actions</h3>
        <div style='background: #2D2D2D; padding: min(1.2em, 4vw); border-radius: 10px;'>
    """, unsafe_allow_html=True)
    
    one_time_actions = [action for action in st.session_state.current_plan['one_time_actions'].split('\n') if action.strip()]
    for i, action in enumerate(one_time_actions, 1):
        st.markdown(f"""
            <div style='display: flex; align-items: flex-start; margin-bottom: 1em; background: #383838; padding: min(1em, 4vw); border-radius: 10px; gap: min(12px, 3vw);'>
                <div style='background: #FF4B4B; color: white; border-radius: 50%; min-width: 28px; height: 28px; 
                           display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: bold;'>
                    {i}
                </div>
                <div style='flex: 1; color: #E0E0E0; line-height: 1.5; font-size: min(1em, 4vw);'>{action}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display daily micro-habits
    st.markdown("""
        <h3 style='color: #FF4B4B; margin: 1.5em 0 1em; text-align: center; font-size: min(1.8em, 7vw);'>✨ Daily Micro-habits</h3>
        <div style='background: #2D2D2D; padding: min(1.2em, 4vw); border-radius: 10px;'>
    """, unsafe_allow_html=True)
    
    habits = [habit for habit in st.session_state.current_plan['habits'].split('\n') if habit.strip()]
    for i, habit in enumerate(habits, 1):
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
    
    # Time commitment input section
    time_commitment = st.text_input("Enter time commitment for your goal (e.g., 30 minutes/day):")
    if time_commitment:
        st.session_state.current_plan['time_commitment'] = time_commitment
    
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
    
    # Generate PDF
    pdf_path = pdf_service.create_pdf(
        goal=st.session_state.current_plan['goal'],
        strategy_points=initiatives,
        one_time_actions=one_time_actions,
        micro_habits=habits
    )
    
    st.markdown(
        get_pdf_download_link(pdf_path, "📥 Download Your Strategic Plan"),
        unsafe_allow_html=True
    )
    
    # Email reminder section
    if not st.session_state.user_email:
        st.markdown("<h3 style='color: #FF4B4B; margin: 1.5em 0 1em; text-align: center;'>📧 Signup for Personalized Email Reminders on your goal and to download our habits tracker</h3>", unsafe_allow_html=True)
        email = st.text_input("Enter your email address:")
        
        # Add description of benefits
        st.markdown("""
            <div style='background: #f0f2f6; padding: 1em; border-radius: 5px; margin: 1em 0;'>
                <p style='color: #666; margin-bottom: 0.5em;'>✨ By signing up, you'll get:</p>
                <ul style='color: #666; margin: 0;'>
                    <li>Daily tracking of your progress</li>
                    <li>Personalized motivation messages</li>
                    <li>Smart reminder emails</li>
                    <li>Access to our habits tracker</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Save My Plan and Sign Up"):
            if is_valid_email(email):
                # Try to sign up the user
                success, message = user_service.sign_up_with_email(email)
                if success:
                    st.session_state.user_email = email
                    # Save entries to Firebase
                    save_entries()
                    st.success(message)
                    st.info("Check your email to set up your password and complete your account setup!")
                else:
                    st.error(message)
            else:
                st.error("Please enter a valid email address.")
    
    # Save all entries regardless of button click
    save_entries()  # Call the function to save all entries

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
