import streamlit as st
from pathlib import Path
from services.openai_service import OpenAIService
from services.firebase_service import FirebaseService
from components.welcome import show_welcome_section
from utils.session import init_session_state, is_valid_email

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

# Initialize services
try:
    openai_service = OpenAIService()  # No need to pass api_key, it will use st.secrets
except Exception as e:
    st.error("Please set your OpenAI API key in .streamlit/secrets.toml")
    st.stop()

try:
    firebase_service = FirebaseService()
except Exception as e:
    st.error(f"Error initializing Firebase: {str(e)}")
    st.stop()

# Load CSS
css_path = Path(__file__).parent / "styles" / "main.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
init_session_state()

# Streamlit app layout
if not st.session_state.current_plan:
    st.session_state.current_step = 1
    show_welcome_section()
    
    # Goal input section
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.markdown("### What's your goal? 🎯")
    st.markdown("""
        <div class='tip-box'>
            <strong>Pro Tip:</strong> Be specific! Instead of "get fit", try "run a 5K in under 30 minutes by March 2024"
        </div>
    """, unsafe_allow_html=True)
    
    goal = st.text_input("", key="goal_input", placeholder="Enter your goal here...", 
                        help="Be specific, measurable, and time-bound")
    
    # Email collection with clear benefits
    st.markdown("""
        <div style='text-align: center; margin: 2em 0 1em;'>
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
        build_plan = st.button(
            "Create My Success Plan →",
            key="build_plan",
            help="Generate your personalized action plan"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if build_plan:
        if not all_questions_answered():
            st.error("🤔 Please answer all questions first!")
            st.stop()
        if time_commitment <= 0:
            st.error("⏰ Please set your daily time commitment!")
            st.stop()

        with st.spinner("🎨 Creating your personalized plan..."):
            answers = {q: st.session_state[f"answer_{i}"] for i, q in enumerate(st.session_state.questions)}
            tasks, habits = openai_service.generate_plan(goal, answers, time_commitment)
            
            st.session_state.current_plan = {
                'goal': goal,
                'questions': st.session_state.questions,
                'answers': answers,
                'time_commitment': time_commitment,
                'tasks': tasks,
                'habits': habits
            }

# Display plan and reminder option
if st.session_state.current_plan and not st.session_state.plan_saved:
    st.session_state.current_step = 3
    
    st.markdown("""
        <div class='celebration-box'>
            <h2 style='color: #FF4B4B; margin: 0.5em 0;'>
                🎉 Your Personalized Success Blueprint is Ready!
            </h2>
            <p style='color: #666; font-size: 1.1em;'>
                We've analyzed your goal and created a strategic plan designed specifically for your success.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class='tip-box'>
            <strong>Pro Tip:</strong> Take a moment to review your plan. Consider how each step fits into your daily routine.
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class='info-box'>
                <h3>🗺️ Your Strategic Action Plan</h3>
                <p>Follow these carefully crafted steps to reach your goal effectively:</p>
                <ul>
                    {points}
                </ul>
            </div>
        """.format(points=''.join(f'<li>{point}</li>' for point in st.session_state.current_plan['tasks'].split('\n') if point.strip())), 
        unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class='info-box'>
                <h3>✨ Success-Building Habits</h3>
                <p>Develop these powerful daily habits to accelerate your progress:</p>
                <ul>
                    {points}
                </ul>
            </div>
        """.format(points=''.join(f'<li>{point}</li>' for point in st.session_state.current_plan['habits'].split('\n') if point.strip())), 
        unsafe_allow_html=True)

    # Reminder setup
    st.session_state.current_step = 4
    
    if hasattr(st.session_state, 'user_email') and st.session_state.user_email:
        st.markdown("""
            <div style='text-align: center;'>
                <h3 style='color: #FF4B4B;'>⏰ Customize Your Success Journey</h3>
                <p style='font-size: 1.1em; max-width: 600px; margin: 1em auto;'>
                    Let's personalize your support system! Choose when you'd like to receive your:
                    <br>• Progress check-ins
                    <br>• Motivation boosts
                    <br>• Achievement celebrations
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class='tip-box'>
                <strong>Pro Tip:</strong> Choose a time when you're most likely to be able to read and act on your reminders.
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("reminder_form"):
            col1, col2 = st.columns(2)
            with col1:
                reminder_frequency = st.selectbox(
                    "How often would you like support? 📅",
                    ["Daily", "Weekly"],
                    index=0
                )
            with col2:
                reminder_time = st.time_input(
                    "Best time for your success check-ins? ⏰",
                    value=None
                )
            
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.markdown("<div class='big-button success-button'>", unsafe_allow_html=True)
                submit_button = st.form_submit_button("🚀 Activate My Success Plan")
                st.markdown("</div>", unsafe_allow_html=True)

            if submit_button:
                reminder_settings = {
                    'email': st.session_state.user_email,
                    'frequency': reminder_frequency,
                    'time': reminder_time.strftime('%H:%M') if reminder_time else None,
                    'status': 'active'
                }
                
                try:
                    goal_id = firebase_service.store_user_goal(
                        goal=st.session_state.current_plan['goal'],
                        questions=st.session_state.current_plan['questions'],
                        answers=st.session_state.current_plan['answers'],
                        time_commitment=st.session_state.current_plan['time_commitment'],
                        tasks=st.session_state.current_plan['tasks'],
                        habits=st.session_state.current_plan['habits'],
                        reminder_settings=reminder_settings
                    )
                    if goal_id:
                        st.session_state.plan_saved = True
                        st.success(f"🎯 Perfect! I'll send you {reminder_frequency.lower()} reminders at {reminder_time.strftime('%I:%M %p')} to keep you motivated!")
                        st.balloons()
                except Exception as e:
                    st.warning(f"Could not save your plan: {str(e)}")
    else:
        # Show email collection if not provided earlier
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center;'>
                <h3 style='color: #FF4B4B;'>🌟 Want to Stay on Track?</h3>
                <p style='font-size: 1.1em;'>
                    Let me be your personal cheerleader! I'll send you friendly reminders to:
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.markdown("""
                <div style='text-align: center; padding: 1em;'>
                    <h4>🎯 Keep You Motivated</h4>
                    <p>Daily encouragement to stay focused on your goals</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <div style='text-align: center; padding: 1em;'>
                    <h4>📝 Track Your Habits</h4>
                    <p>Regular check-ins on your micro-habits</p>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
                <div style='text-align: center; padding: 1em;'>
                    <h4>🎊 Celebrate Progress</h4>
                    <p>Recognition of your achievements</p>
                </div>
            """, unsafe_allow_html=True)
        
        with st.form("email_form"):
            st.markdown("""
                <h3 style='text-align: center; color: #FF4B4B;'>
                    📬 Let's Get Started with Reminders
                </h3>
            """, unsafe_allow_html=True)
            
            late_email = st.text_input(
                "What's your email? (I promise to only send the good stuff! 📨)",
                placeholder="your.email@example.com"
            )
            
            if late_email and not is_valid_email(late_email):
                st.error("Oops! That email doesn't look quite right. Mind double-checking? 🤔")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    reminder_frequency = st.selectbox(
                        "How often should I check in? 📅",
                        ["Daily", "Weekly"],
                        index=0
                    )
                with col2:
                    reminder_time = st.time_input(
                        "Best time to reach you? ⏰",
                        value=None
                    )
            
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.markdown("<div class='big-button success-button'>", unsafe_allow_html=True)
                submit_button = st.form_submit_button("🚀 Let's Do This!")
                st.markdown("</div>", unsafe_allow_html=True)
            
            if submit_button:
                if not late_email or not is_valid_email(late_email):
                    st.error("Please enter a valid email address!")
                    st.stop()
                    
                reminder_settings = {
                    'email': late_email,
                    'frequency': reminder_frequency,
                    'time': reminder_time.strftime('%H:%M') if reminder_time else None,
                    'status': 'active'
                }
                
                try:
                    goal_id = firebase_service.store_user_goal(
                        goal=st.session_state.current_plan['goal'],
                        questions=st.session_state.current_plan['questions'],
                        answers=st.session_state.current_plan['answers'],
                        time_commitment=st.session_state.current_plan['time_commitment'],
                        tasks=st.session_state.current_plan['tasks'],
                        habits=st.session_state.current_plan['habits'],
                        reminder_settings=reminder_settings
                    )
                    if goal_id:
                        st.session_state.plan_saved = True
                        st.success(f"🎯 You're all set! I'll send you {reminder_frequency.lower()} reminders at {reminder_time.strftime('%I:%M %p')} to keep you on track!")
                        st.balloons()
                except Exception as e:
                    st.warning(f"Could not save your plan: {str(e)}")

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
