import openai
import streamlit as st
from typing import Dict, Optional
from services.security_service import SecurityService
from config.prompts import GOAL_REFINEMENT_CONFIG, GOAL_FINAL_REFINEMENT_CONFIG

class GoalRefinementService:
    def __init__(self):
        self.security = SecurityService()
        openai.api_key = st.secrets["OPENAI_API_KEY"]  # Use the same API key from secrets
        
        self.refinement_config = GOAL_REFINEMENT_CONFIG
        self.final_refinement_config = GOAL_FINAL_REFINEMENT_CONFIG

    def get_refinement_questions(self, initial_goal: str) -> Optional[str]:
        """Generate refinement questions based on the initial goal."""
        try:
            # Sanitize input
            initial_goal = self.security.sanitize_input(initial_goal)
            
            st.write("DEBUG - Initial goal:", initial_goal)  # Debug log
            
            response = openai.ChatCompletion.create(
                model=self.refinement_config["model"],
                messages=[
                    {"role": "system", "content": self.refinement_config["system_role"]},
                    {"role": "user", "content": self.refinement_config["prompt"]},
                    {"role": "user", "content": initial_goal}
                ],
                temperature=0.7
            )
            
            questions = response.choices[0].message.content
            st.write("DEBUG - Generated questions:", questions)  # Debug log
            return questions
            
        except Exception as e:
            st.error(f"Error generating refinement questions: {str(e)}")
            return None

    def generate_refined_goal(self, initial_goal: str, user_responses: str) -> Optional[str]:
        """Generate the final refined goal based on initial goal and user responses."""
        try:
            # Sanitize inputs
            initial_goal = self.security.sanitize_input(initial_goal)
            user_responses = self.security.sanitize_input(user_responses)
            
            st.write("DEBUG - Generating refined goal")  # Debug log
            st.write("Initial goal:", initial_goal)
            st.write("User responses:", user_responses)
            
            prompt = f"""Initial Goal: {initial_goal}
User's Additional Information: {user_responses}"""
            
            response = openai.ChatCompletion.create(
                model=self.final_refinement_config["model"],
                messages=[
                    {"role": "system", "content": self.final_refinement_config["system_role"]},
                    {"role": "user", "content": self.final_refinement_config["prompt"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            refined_goal = response.choices[0].message.content
            st.write("DEBUG - Generated refined goal:", refined_goal)  # Debug log
            return refined_goal
            
        except Exception as e:
            st.error(f"Error generating refined goal: {str(e)}")
            return None
