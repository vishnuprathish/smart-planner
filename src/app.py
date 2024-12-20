import streamlit as st
import openai
import os
from services.openai_service import OpenAIService
from services.firebase_service import FirebaseService
from utils.constants import *

# Initialize OpenAI client
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except Exception as e:
    st.error("Please set your OpenAI API key in .streamlit/secrets.toml")
    st.stop()

# Initialize services
openai_service = OpenAIService(openai.api_key)
try:
    firebase_service = FirebaseService()
except Exception as e:
    st.error(f"Error initializing Firebase: {str(e)}")
    st.stop()

# Streamlit app layout
st.title(APP_TITLE)

# Initialize session state
if 'questions' not in st.session_state:
    st.session_state.questions = None
if 'show_questions' not in st.session_state:
    st.session_state.show_questions = False
if 'goal' not in st.session_state:
    st.session_state.goal = None

def all_questions_answered():
    """Check if all questions have been answered."""
    if not st.session_state.questions:
        return False
    return all(st.session_state.get(f"answer_{i}") for i in range(len(st.session_state.questions)))

# Text box for user input
user_input = st.text_input(ENTER_GOAL_MESSAGE, key="goal")

# Button to generate questions
if st.button('Get Started'):
    if user_input:
        with st.spinner('Generating relevant questions...'):
            st.session_state.questions = openai_service.generate_questions(user_input)
            st.session_state.show_questions = True
    else:
        st.warning(MISSING_GOAL_WARNING)

# Display questions and collect answers
if st.session_state.show_questions and st.session_state.questions:
    st.write(QUESTIONS_HEADING)
    
    # Display questions and collect answers
    for i, q in enumerate(st.session_state.questions):
        st.text_input(q, key=f"answer_{i}")
    
    # Time commitment input
    time_commitment = st.number_input(
        TIME_COMMITMENT_MESSAGE,
        min_value=MIN_DAILY_MINUTES,
        max_value=MAX_DAILY_MINUTES,
        value=DEFAULT_DAILY_MINUTES,
        step=TIME_STEP_MINUTES,
        help=TIME_COMMITMENT_HELP
    )

    # Button to generate plan
    if st.button('Build my plan'):
        if not user_input:
            st.error("Please enter your goal first!")
            st.stop()
        if not all_questions_answered():
            st.error("Please answer all questions first!")
            st.stop()
        if time_commitment <= 0:
            st.error("Please set your daily time commitment!")
            st.stop()

        with st.spinner('Generating your personalized plan...'):
            # Get answers from session state
            answers = {q: st.session_state[f"answer_{i}"] for i, q in enumerate(st.session_state.questions)}
            
            # Generate the plan
            tasks, habits = openai_service.generate_plan(user_input, answers, time_commitment)
            
            # Store in Firebase
            try:
                goal_id = firebase_service.store_user_goal(
                    goal=user_input,
                    questions=st.session_state.questions,
                    answers=answers,
                    time_commitment=time_commitment,
                    tasks=tasks,
                    habits=habits
                )
                if goal_id:
                    st.success("Your plan has been saved!")
            except Exception as e:
                st.warning(f"Could not save your plan: {str(e)}")
            
            # Display the plan
            st.subheader("Your Action Plan:")
            st.write(tasks)
            
            st.subheader("Daily Micro-habits:")
            st.write(habits)

# Add a section to view previous goals
if st.sidebar.checkbox("View Previous Goals"):
    st.sidebar.subheader("Previous Goals")
    try:
        goals = firebase_service.get_user_goals()
        if goals:
            for goal in goals:
                with st.sidebar.expander(f"Goal: {goal['goal'][:50]}..."):
                    st.write(f"Time Commitment: {goal['time_commitment']} minutes/day")
                    st.write("Tasks:")
                    st.write(goal['tasks'])
                    st.write("Habits:")
                    st.write(goal['habits'])
                    st.write(f"Created: {goal['timestamp']}")
        else:
            st.sidebar.info("No previous goals found.")
    except Exception as e:
        st.sidebar.error(f"Error loading previous goals: {str(e)}")
