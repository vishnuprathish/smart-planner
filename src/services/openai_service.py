import openai
import streamlit as st
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import json
import os
from pathlib import Path
from config.prompts import QUESTIONS_CONFIG, PLAN_CONFIG
from services.security_service import SecurityService

class GoalPlan(BaseModel):
    """Schema for the goal plan response."""
    strategic_initiatives: List[str] = Field(
        min_items=3,
        max_items=5,
        description="List of 3-5 strategic initiatives to achieve the goal"
    )
    one_time_actions: List[str] = Field(
        min_items=2,
        max_items=5,
        description="List of 2-5 one-time setup actions to get started"
    )
    habits: List[str] = Field(
        min_items=3,
        max_items=7,
        description="List of 3-7 daily micro-habits that support the goal"
    )

class OpenAIService:
    def __init__(self, api_key=None):
        """Initialize OpenAI service with API key."""
        self.security = SecurityService()
        api_key = api_key or st.secrets["OPENAI_API_KEY"]
        openai.api_key = api_key

    def generate_questions(self, goal: str) -> List[str]:
        """Generate relevant questions based on the user's goal."""
        try:
            # Check rate limit using session ID
            if self.security.is_rate_limited(str(id(st.session_state))):
                st.error("Rate limit exceeded. Please try again later.")
                return []
                
            # Sanitize input
            goal = self.security.sanitize_input(goal)
            if not goal:
                st.error("Invalid input provided")
                return []
            
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
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                st.error("Error processing OpenAI response. Please try again.")
                return []
                
        except openai.error.APIError as e:
            st.error("OpenAI API error. Please try again in a few moments.")
            return []
        except openai.error.Timeout as e:
            st.error("Request timed out. Please try again.")
            return []
        except openai.error.RateLimitError as e:
            st.error("Rate limit exceeded. Please try again in a few moments.")
            return []
        except openai.error.APIConnectionError as e:
            st.error("""
                Unable to connect to OpenAI. Please check your internet connection and try:
                1. Refreshing the page
                2. Checking if you're connected to the internet
                3. Waiting a few moments and trying again
            """)
            return []
        except Exception as e:
            st.error(f"An unexpected error occurred. Please try again.")
            return []

    def generate_plan(self, goal: str, questions: List[str], answers: List[str]) -> Optional[Dict]:
        """Generate a personalized action plan based on the user's goal and answers."""
        try:
            # Check rate limit using session ID
            if self.security.is_rate_limited(str(id(st.session_state))):
                st.error("Rate limit exceeded. Please try again later.")
                return None
                
            # Sanitize all inputs
            goal = self.security.sanitize_input(goal)
            questions = [self.security.sanitize_input(q) for q in questions]
            answers = [self.security.sanitize_input(a) for a in answers]
            
            if not all([goal, questions, answers]):
                st.error("Invalid input provided")
                return None
                
            # Combine questions and answers
            qa_pairs = [f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)]
            qa_text = "\n\n".join(qa_pairs)
            
            response = openai.ChatCompletion.create(
                model=PLAN_CONFIG.model,
                messages=[
                    {"role": "system", "content": PLAN_CONFIG.system_prompt},
                    {"role": "user", "content": PLAN_CONFIG.user_prompt_template.format(
                        goal=goal,
                        answers=qa_text
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
                    'one_time_actions': '\n'.join(plan.one_time_actions),
                    'habits': '\n'.join(plan.habits)
                }
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                st.error("Error processing the plan. Please try again.")
                return None
                
        except openai.error.APIError as e:
            st.error("OpenAI API error. Please try again in a few moments.")
            return None
        except openai.error.Timeout as e:
            st.error("Request timed out. Please try again.")
            return None
        except openai.error.RateLimitError as e:
            st.error("Rate limit exceeded. Please try again in a few moments.")
            return None
        except openai.error.APIConnectionError as e:
            st.error("""
                Unable to connect to OpenAI. Please check your internet connection and try:
                1. Refreshing the page
                2. Checking if you're connected to the internet
                3. Waiting a few moments and trying again
            """)
            return None
        except Exception as e:
            st.error(f"An unexpected error occurred. Please try again.")
            return None
