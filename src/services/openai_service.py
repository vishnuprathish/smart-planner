import openai
from typing import Tuple, List

class OpenAIService:
    def __init__(self, api_key: str):
        """Initialize OpenAI service with API key."""
        openai.api_key = api_key

    def generate_questions(self, goal: str) -> List[str]:
        """Generate relevant questions based on the goal."""
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

    def generate_plan(self, goal: str, answers: dict, time_commitment: int) -> Tuple[str, str]:
        """Generate task breakdown and micro-habits based on goal and answers."""
        context = f"""Goal: {goal}\n\nAdditional Information:"""
        for q, a in answers.items():
            context += f"\n{q}\nAnswer: {a}"
        context += f"\nDaily time commitment: {time_commitment} minutes per day"
        
        try:
            # Generate task breakdown
            tasks_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates detailed, personalized action plans."},
                    {"role": "user", "content": f"Based on the following goal and additional information, create a detailed, actionable task breakdown:\n\n{context}\n\nProvide a numbered list of specific, actionable tasks."}
                ]
            )
            tasks = tasks_response.choices[0].message.content

            # Generate micro-habits
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
