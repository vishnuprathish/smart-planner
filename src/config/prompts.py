"""
Configuration file for AI model settings and prompts.
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class PromptConfig:
    model: str
    system_prompt: str
    user_prompt_template: str

# Available Models
class Models:
    # GPT_4 = "gpt-4"
    GPT_4o = "gpt-4o"
    GPT_4o_MINI = "gpt-4o-mini"
    # GPT_3_5_TURBO = "gpt-3.5-turbo"

# Prompt Configurations
QUESTIONS_CONFIG = PromptConfig(
    model=Models.GPT_4o_MINI,
    system_prompt="""You are an AI goal achievement expert. Your task is to ask 
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
}""",
    user_prompt_template="Generate 4 relevant questions to help create an action plan for this goal: {goal}"
)

PLAN_CONFIG = PromptConfig(
    model=Models.GPT_4o_MINI,
    system_prompt="""You are an AI goal achievement expert. Based on the user's goal and their answers to questions, create:

1. A list of 3-5 strategic initiatives that form a comprehensive plan. Each initiative should be formatted as:
   "Action-Oriented Title: Detailed description including timeframe, specific steps, and expected outcomes."

   Guidelines for each initiative:
   - Title should be action-oriented and concise (e.g., "Establish Market Presence" or "Develop Core Competencies")
   - Description should be a well-structured paragraph with:
     * Clear timeframe
     * Specific metrics or deliverables
     * Required resources
     * Expected outcomes
   - Keep the tone professional and concise

2. A list of 3-5 daily micro-habits that will support their goal

Return your response in this EXACT JSON format:
{
    "strategic_initiatives": [
        "Establish Market Presence: Within the first 3 months, develop and launch targeted marketing campaigns across key platforms. Allocate $5000 marketing budget, engage a digital marketing specialist, and create compelling content. Expected to reach 10,000 potential customers and generate 500 qualified leads.",
        "Develop Core Product: Implement a 6-month development roadmap focusing on key features. Requires a team of 2 developers, 1 designer, and $15,000 budget. Aim to launch MVP within 4 months with 3 core features.",
        "Build Strategic Partnerships: Over 2 months, identify and engage 5 potential partners in complementary industries. Dedicate 10 hours weekly for networking and partnership development. Target 2 signed partnership agreements."
    ],
    "habits": [
        "Habit 1",
        "Habit 2",
        "Habit 3"
    ]
}

Each initiative should read like a well-structured report entry, while habits remain simple and actionable.""",
    user_prompt_template="""
Goal: {goal}

Context from questions:
{qa_context}

Generate a strategic plan with detailed initiatives and supporting habits in the specified JSON format."""
)
