import streamlit as st
from services.openai_service import OpenAIService
from utils.constants import *

# Initialize OpenAI service
openai_service = OpenAIService(st.secrets["OPENAI_API_KEY"])

# Streamlit app layout
st.title(APP_TITLE)

# Initialize session state for questions
if 'questions' not in st.session_state:
    st.session_state.questions = None
if 'show_questions' not in st.session_state:
    st.session_state.show_questions = False

# Text box for user input
user_input = st.text_input(ENTER_GOAL_MESSAGE)

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
    answers = {}
    for q in st.session_state.questions:
        answers[q] = st.text_input(q, key=q)
    
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
        if all(answers.values()):  # Check if all questions are answered
            with st.spinner('Generating your personalized plan...'):
                tasks, habits = openai_service.generate_plan(user_input, answers, time_commitment)
                
                st.write(TASK_BREAKDOWN_HEADING)
                st.write(tasks)
                
                st.write(MICRO_HABITS_HEADING)
                st.write(habits)
                
                # Add a note about consistency
                st.info(CONSISTENCY_MESSAGE)
        else:
            st.warning(MISSING_ANSWERS_WARNING)
