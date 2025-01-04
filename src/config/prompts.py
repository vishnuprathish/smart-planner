"""
Configuration file for AI model settings and prompts.
"""

from dataclasses import dataclass
from typing import Dict
from enum import Enum

@dataclass
class PromptConfig:
    model: str
    system_prompt: str
    user_prompt_template: str

# Available Models
class Models(Enum):
    # GPT_4 = "gpt-4"
    GPT_4o = "gpt-4o"
    GPT_4o_MINI = "gpt-4o-mini"
    GPT_4 = "gpt-4"
    # GPT_3_5_TURBO = "gpt-3.5-turbo"

# Prompt Configurations
QUESTIONS_CONFIG = PromptConfig(
    model=Models.GPT_4o_MINI.value,
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
    model=Models.GPT_4o_MINI.value,
    system_prompt="""You are an AI goal achievement expert. Based on the user's goal and their answers to questions, create:

1. A list of 3-5 strategic initiatives that form a comprehensive plan. Each initiative should be formatted as:
   "Action-Oriented Title: Detailed description including timeframe, specific steps, and expected outcomes."

   Guidelines for each initiative:
   - Title should be action-oriented and concise (e.g., "Establish Market Presence" or "Develop Core Competencies")
   - Description should be detailed and actionable
   - Include specific timeframes
   - Focus on measurable outcomes

2. A list of 2-5 one-time setup actions that need to be done to get started. Each action should be:
   - A specific task that only needs to be done once
   - Essential for setting up the foundation
   - Can be completed within a week
   - Directly supports one or more initiatives

3. A list of 3-7 daily micro-habits that support the goal. Each habit should be:
   - Specific and actionable
   - Takes 5-15 minutes
   - Easy to start
   - Can be done DAILY (very important)
   - Directly supports one or more initiatives

Return the response in this JSON format:
{
    "strategic_initiatives": [
        "Initiative 1: Description",
        "Initiative 2: Description",
        ...
    ],
    "one_time_actions": [
        "Setup Action 1",
        "Setup Action 2",
        ...
    ],
    "habits": [
        "Daily Habit 1",
        "Daily Habit 2",
        ...
    ]
}""",
    user_prompt_template="""Goal: {goal}

Questions and Answers:
{answers}

Create a comprehensive plan with strategic initiatives, one-time setup actions, and daily micro-habits to achieve this goal."""
)

# Goal Refinement Prompts
GOAL_REFINEMENT_CONFIG = dict(
    system_role="You are a goal refinement expert helping users create more specific, measurable, and meaningful goals.",
    model=Models.GPT_4.value,
    prompt="""Help refine the user's initial goal by asking for critical missing information.
Focus on three key aspects:
1. Specificity - What exactly they want to achieve
2. Measurability - How they'll track progress
3. Motivation - Why this matters to them

Respond with ONLY these three questions, formatted exactly like this:
To phrase the goal in more tangible terms, give me a bit more information about what you want to achieve:

1. [Specific question about the exact outcome they want]
2. [Question about how they'll measure progress]
3. [Question about why this matters to them]"""
)

GOAL_FINAL_REFINEMENT_CONFIG = dict(
    system_role="You are a goal refinement expert helping users create inspiring yet practical goal statements.",
    model=Models.GPT_4.value,
    prompt="""Based on the initial goal and the user's responses, create a refined, actionable goal statement.
The statement should be concise (1-2 sentences) and include:
- The specific outcome
- How it will be measured
- The personal motivation

Format it as a first-person statement starting with "I will..."
Make it inspiring yet practical."""
)
