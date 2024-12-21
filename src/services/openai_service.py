from openai import OpenAI
import streamlit as st
from typing import List, Dict
from pydantic import BaseModel, Field
import json

class GoalPlan(BaseModel):
    """Schema for the goal plan response."""
    tasks: List[str] = Field(
        min_items=3,
        max_items=5,
        description="List of 3-5 strategic action items to achieve the goal"
    )
    habits: List[str] = Field(
        min_items=3,
        max_items=5,
        description="List of 3-5 daily micro-habits that support the goal"
    )

class OpenAIService:
    def __init__(self, api_key=None):
        """Initialize OpenAI service with API key."""
        try:
            self.api_key = api_key or st.secrets["OPENAI_API_KEY"]
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            raise Exception("Please set your OpenAI API key in .streamlit/secrets.toml")

    def generate_questions(self, goal: str) -> List[str]:
        """Generate relevant questions based on the user's goal."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are an AI goal achievement expert. Your task is to ask 
                     relevant questions that will help create a personalized action plan. Ask questions about:
                     1. Current situation and starting point
                     2. Specific challenges or obstacles
                     3. Previous attempts or experience
                     4. Available resources and support
                     
                     Return EXACTLY 4 questions in this JSON format:
                     {
                         "questions": [
                             "Question 1",
                             "Question 2",
                             "Question 3",
                             "Question 4"
                         ]
                     }"""},
                    {"role": "user", "content": f"Generate 4 relevant questions to help create an action plan for this goal: {goal}"}
                ]
            )
            
            try:
                # Parse JSON response
                response_data = json.loads(response.choices[0].message.content)
                questions = response_data.get("questions", [])
                return questions[:4]
            except json.JSONDecodeError:
                # Fallback: split by newlines if JSON parsing fails
                questions = response.choices[0].message.content.split('\n')
                questions = [q.strip().replace('*', '').replace('-', '').strip() 
                           for q in questions if q.strip()]
                return questions[:4]
            
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            return []

    def generate_plan(self, goal: str, questions: List[str], answers: List[str]) -> Dict:
        """Generate a personalized action plan based on the user's goal and answers."""
        try:
            # Combine questions and answers
            qa_pairs = [f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)]
            qa_context = "\n\n".join(qa_pairs)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are an AI goal achievement expert. Based on the user's goal and their answers to questions, create:
                     1. A list of 3-5 strategic action items (tasks)
                     2. A list of 3-5 daily micro-habits that will support their goal
                     
                     Return your response in this EXACT JSON format:
                     {
                         "tasks": [
                             "Task 1",
                             "Task 2",
                             "Task 3"
                         ],
                         "habits": [
                             "Habit 1",
                             "Habit 2",
                             "Habit 3"
                         ]
                     }
                     
                     Each task should be specific, actionable, and aligned with their goal.
                     Each habit should be small, manageable, and directly support their goal.
                     """},
                    {"role": "user", "content": f"""
                    Goal: {goal}
                    
                    Context from questions:
                    {qa_context}
                    
                    Generate a strategic plan with tasks and habits in the specified JSON format.
                    """}
                ]
            )
            
            try:
                # Parse and validate response
                response_data = json.loads(response.choices[0].message.content)
                plan = GoalPlan(**response_data)
                
                return {
                    'goal': goal,
                    'questions': questions,
                    'answers': answers,
                    'tasks': '\n'.join(plan.tasks),
                    'habits': '\n'.join(plan.habits)
                }
            except json.JSONDecodeError as e:
                st.error("Error: The AI response was not in the correct format. Please try again.")
                return None
            
        except Exception as e:
            st.error(f"Error generating plan: {str(e)}")
            return None
