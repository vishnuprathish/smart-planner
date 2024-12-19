import streamlit as st
import openai
import os

# Set the provided local time
local_time = '2024-12-19T14:00:27-05:00'

# Initialize OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Streamlit app layout
st.title('Smart Goal Planner')

# Initialize session state for questions
if 'questions' not in st.session_state:
    st.session_state.questions = None
if 'show_questions' not in st.session_state:
    st.session_state.show_questions = False

def generate_questions(goal):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates relevant questions to better understand someone's goal."},
                {"role": "user", "content": f"Generate exactly 3 specific questions that would help better understand the following goal: {goal}. Return only the questions, numbered 1-3, nothing else."}
            ]
        )
        return response.choices[0].message.content.strip().split('\n')
    except Exception as e:
        return [f"Error generating questions: {str(e)}"]

def generate_task_breakdown(goal, answers, time_commitment):
    context = f"""Goal: {goal}\n\nAdditional Information:"""
    for q, a in answers.items():
        context += f"\n{q}\nAnswer: {a}"
    context += f"\nDaily time commitment: {time_commitment} minutes per day"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates detailed, personalized action plans."},
                {"role": "user", "content": f"Based on the following goal and additional information, create a detailed, actionable task breakdown:\n\n{context}\n\nProvide a numbered list of specific, actionable tasks."}
            ]
        )
        tasks = response.choices[0].message.content

        # Generate micro-habits based on tasks
        habits_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that converts tasks into daily micro-habits."},
                {"role": "user", "content": f"""Based on these tasks and the time commitment of {time_commitment} minutes per day, create a set of daily micro-habits that will help achieve the goal.
                
Tasks:
{tasks}

Convert these into 3-5 specific daily micro-habits that:
1. Can fit within the {time_commitment} minutes per day time commitment
2. Are specific and measurable
3. Start with small, achievable steps
4. Can be done consistently every day

Format as: 'Daily Micro-habits:' followed by a numbered list."""}
            ]
        )
        
        return tasks, habits_response.choices[0].message.content
    except Exception as e:
        return f"Error generating plan: {str(e)}", ""

# Text box for user input
user_input = st.text_input('Enter a goal you want to achieve:')

# Button to generate questions
if st.button('Get Started'):
    if user_input:
        with st.spinner('Generating relevant questions...'):
            st.session_state.questions = generate_questions(user_input)
            st.session_state.show_questions = True
    else:
        st.warning('Please enter a goal first!')

# Display questions and collect answers
if st.session_state.show_questions and st.session_state.questions:
    st.write("### Please answer these questions to help create a better plan:")
    answers = {}
    for q in st.session_state.questions:
        answers[q] = st.text_input(q, key=q)
    
    # Time commitment input
    time_commitment = st.number_input('How many minutes per day can you commit to this goal?', 
                                    min_value=5, 
                                    max_value=240, 
                                    value=30,
                                    step=5,
                                    help="Choose between 5 and 240 minutes")
    
    # Button to generate plan
    if st.button('Build my plan'):
        if all(answers.values()):  # Check if all questions are answered
            with st.spinner('Generating your personalized plan...'):
                tasks, habits = generate_task_breakdown(user_input, answers, time_commitment)
                
                st.write("### Here's your personalized task breakdown:")
                st.write(tasks)
                
                st.write("### Your Daily Micro-habits:")
                st.write(habits)
                
                # Add a note about consistency
                st.info("💡 Remember: The key to success is consistency. Start small and build up gradually!")
        else:
            st.warning('Please answer all questions before generating the plan.')
