import openai
import streamlit as st
from typing import List, Dict
from pydantic import BaseModel, Field
import json
import os
from pathlib import Path
from config.prompts import QUESTIONS_CONFIG, PLAN_CONFIG

class GoalPlan(BaseModel):
    """Schema for the goal plan response."""
    strategic_initiatives: List[str] = Field(
        min_items=3,
        max_items=5,
        description="List of 3-5 strategic initiatives to achieve the goal"
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
            # Try to get API key from environment first
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            
            # If not in environment, try to get from secrets file
            if not self.api_key:
                secrets_path = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"
                if secrets_path.exists():
                    with open(secrets_path, 'r') as f:
                        for line in f:
                            if line.startswith("OPENAI_API_KEY"):
                                self.api_key = line.split("=")[1].strip().strip('"').strip("'")
                                break
            
            if not self.api_key:
                raise Exception("OpenAI API key not found")
                
            # Set the API key for the openai module
            openai.api_key = self.api_key
            
        except Exception as e:
            raise Exception(f"Error initializing OpenAI service: {str(e)}")

    def generate_questions(self, goal: str) -> List[str]:
        """Generate relevant questions based on the user's goal."""
        try:
            response = openai.ChatCompletion.create(
                model=QUESTIONS_CONFIG.model,
                messages=[
                    {"role": "system", "content": QUESTIONS_CONFIG.system_prompt},
                    {"role": "user", "content": QUESTIONS_CONFIG.user_prompt_template.format(goal=goal)}
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
            
            response = openai.ChatCompletion.create(
                model=PLAN_CONFIG.model,
                messages=[
                    {"role": "system", "content": PLAN_CONFIG.system_prompt},
                    {"role": "user", "content": PLAN_CONFIG.user_prompt_template.format(
                        goal=goal,
                        qa_context=qa_context
                    )}
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
                    'initiatives': '\n'.join(plan.strategic_initiatives),
                    'habits': '\n'.join(plan.habits)
                }
            except json.JSONDecodeError as e:
                st.error("Error: The AI response was not in the correct format. Please try again.")
                return None
            
        except Exception as e:
            st.error(f"Error generating plan: {str(e)}")
            return None
