import openai
import streamlit as st
from typing import Tuple, List

class OpenAIService:
    def __init__(self, api_key=None):
        """Initialize OpenAI service with API key."""
        try:
            self.api_key = api_key or st.secrets["OPENAI_API_KEY"]
            openai.api_key = self.api_key
        except Exception as e:
            raise Exception("Please set your OpenAI API key in .streamlit/secrets.toml")

    def generate_questions(self, goal: str) -> List[str]:
        """Generate relevant questions based on the user's goal."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are an AI goal achievement expert. Your task is to ask 
                     relevant questions that will help create a personalized action plan. Ask questions about:
                     1. Current situation and starting point
                     2. Specific challenges or obstacles
                     3. Previous attempts or experience
                     4. Available resources and support
                     5. Preferred learning style or approach
                     Keep questions concise and focused."""},
                    {"role": "user", "content": f"Generate 5 relevant questions to help create an action plan for this goal: {goal}"}
                ]
            )
            questions = response.choices[0].message.content.split('\n')
            # Clean up question format
            questions = [q.strip().replace('*', '').replace('-', '').strip() for q in questions if q.strip()]
            return questions[:5]  # Ensure we only return 5 questions
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            return []

    def clean_point(self, point: str) -> str:
        """Clean a single point by removing bullets and extra whitespace."""
        # Remove bullet points and their variations
        point = point.strip()
        point = point.lstrip('•').lstrip('*').lstrip('-').lstrip('○').lstrip('·')
        # Remove "First/Second/etc point:" prefixes
        prefixes = ['first', 'second', 'third', 'fourth', 'fifth']
        point_lower = point.lower()
        for prefix in prefixes:
            if point_lower.startswith(f"{prefix} point:"):
                point = point[len(f"{prefix} point:"):].strip()
            elif point_lower.startswith(f"{prefix}:"):
                point = point[len(f"{prefix}:"):].strip()
        return point.strip()

    def generate_plan(self, goal: str, answers: dict, time_commitment: int) -> Tuple[str, str]:
        """Generate a personalized action plan based on the goal and answers."""
        try:
            # Combine answers into a single string
            answers_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in answers.items()])
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are an AI goal achievement expert. Create a personalized action 
                     plan that includes:
                     1. A clear strategy broken down into actionable steps
                     2. Specific micro-habits that can be done in the time commitment specified
                     3. Tips for overcoming potential obstacles
                     4. Ways to track progress
                     Keep the plan practical and achievable.
                     
                     Format your response exactly like this:
                     Strategic Action Plan:
                     • First strategy point
                     • Second strategy point
                     • Third strategy point
                     
                     Success-Building Habits (X mins/day):
                     • First habit
                     • Second habit
                     • Third habit"""},
                    {"role": "user", "content": f"""Create a personalized action plan for this goal: {goal}
                     Time commitment: {time_commitment} minutes per day
                     User's responses:
                     {answers_text}"""}
                ]
            )
            
            full_plan = response.choices[0].message.content
            
            # Split into strategy and habits sections
            sections = full_plan.split('\n\n')
            
            # Extract strategy section
            strategy_section = next((s for s in sections if 'Strategic Action Plan:' in s), '')
            strategy = strategy_section.replace('Strategic Action Plan:', '').strip()
            
            # Extract habits section
            habits_section = next((s for s in sections if 'Success-Building Habits' in s), '')
            habits = habits_section.replace(f'Success-Building Habits ({time_commitment} mins/day):', '').strip()
            
            # Split into bullet points and clean them
            strategy_points = [self.clean_point(point) for point in strategy.split('\n') if point.strip()]
            habits_points = [self.clean_point(point) for point in habits.split('\n') if point.strip()]
            
            # Format as strings with bullet points
            strategy_formatted = '\n'.join(f'• {point}' for point in strategy_points if point)
            habits_formatted = '\n'.join(f'• {point}' for point in habits_points if point)
            
            return strategy_formatted, habits_formatted
            
        except Exception as e:
            st.error(f"Error generating plan: {str(e)}")
            return "", ""
