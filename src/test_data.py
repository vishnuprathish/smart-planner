"""Test data for Smart Goal Planner application."""

test_goals = {
    "fitness": {
        "goal": "Run a 5K race in under 30 minutes by March 2024",
        "answers": {
            "motivation": "I want to improve my overall fitness and challenge myself to accomplish something I've never done before. Running has always been difficult for me, and completing a 5K under 30 minutes would be a significant personal achievement.",
            "obstacles": "Time management with work schedule, potential weather constraints during winter training, and maintaining consistency with training schedule. Also concerned about possible injuries from overtraining.",
            "resources": "Access to a local gym with treadmills, running trails in my neighborhood, and running shoes. I also have a fitness tracking watch and supportive friends who run regularly.",
            "tracking": "Using my fitness watch to track run times and distances, keeping a training log in a fitness app, and doing timed trial runs every two weeks to measure improvement.",
            "current_situation": "Currently can run 2.5K in about 18 minutes, running 2-3 times per week inconsistently. Haven't participated in any organized races before."
        }
    },
    "career": {
        "goal": "Get promoted to Senior Software Engineer by December 2024",
        "answers": {
            "motivation": "I want to take on more leadership responsibilities and contribute to larger technical decisions. The promotion would also validate my growth as a developer and increase my earning potential.",
            "obstacles": "Limited opportunities for technical leadership in current projects, competition from peers, and need to improve system design skills. Also balancing learning time with current work responsibilities.",
            "resources": "Company learning platform subscription, supportive team lead willing to mentor, internal tech talks and workshops, and budget for professional development courses.",
            "tracking": "Monthly 1:1s with manager to discuss growth, keeping a project impact log, tracking completed technical certifications, and collecting peer feedback.",
            "current_situation": "Mid-level developer with 3 years experience, leading one small project team, received \"meets expectations\" in last performance review."
        }
    },
    "finance": {
        "goal": "Save $20,000 for a house down payment by January 2025",
        "answers": {
            "motivation": "Want to stop renting and build equity in my own home. Looking to settle down in a stable living situation and have more control over my living space.",
            "obstacles": "Current high rent payments limiting saving ability, occasional unexpected expenses, and temptation to spend on non-essentials. Also worried about market changes affecting house prices.",
            "resources": "Stable job with regular income, basic understanding of budgeting, access to financial planning tools, and potential for overtime work.",
            "tracking": "Monthly budget review, tracking savings account growth, using expense tracking app, and quarterly financial health check-ins.",
            "current_situation": "Currently have $3,000 saved, spending about 40% of income on rent, and saving approximately $500 per month."
        }
    }
}

def get_test_goal(goal_type: str) -> dict:
    """Get a test goal and its answers.
    
    Args:
        goal_type: One of 'fitness', 'career', or 'finance'
        
    Returns:
        Dictionary containing the goal and its answers
    """
    return test_goals.get(goal_type.lower())

def get_all_test_goals() -> dict:
    """Get all test goals."""
    return test_goals

# Example usage:
if __name__ == "__main__":
    # Print all available test goals
    print("Available test goals:")
    for goal_type, data in test_goals.items():
        print(f"\n{goal_type.upper()} GOAL:")
        print(f"Goal: {data['goal']}")
        print("\nAnswers:")
        for question, answer in data['answers'].items():
            print(f"\n{question.replace('_', ' ').title()}:")
            print(answer)
