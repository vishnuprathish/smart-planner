"""Test data for Smart Goal Planner application."""

test_goals = {
    "fitness": {
        "initial_goal": "I want to get in better shape",
        "refinement_response": "I want to focus on running, specifically completing a 5K race. I'll measure success by my race time, aiming for under 30 minutes. This matters because I want to prove to myself I can achieve a challenging fitness goal by March 2024.",
        "refined_goal": "I will complete a 5K race in under 30 minutes by March 2024, transforming from a casual runner to a competitive racer—because proving my ability to achieve challenging fitness goals is important for my personal growth.",
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
        "initial_goal": "I want to advance in my software engineering career",
        "refinement_response": "I'm aiming for a Senior Software Engineer position. I'll measure success by leading technical projects and mentoring junior developers. This matters because I want to grow my technical leadership skills and increase my impact by December 2024.",
        "refined_goal": "I will earn a promotion to Senior Software Engineer by December 2024 by successfully leading technical projects and mentoring junior developers—because expanding my influence and technical leadership will drive both personal growth and team success.",
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
        "initial_goal": "I want to buy a house",
        "refinement_response": "I need to save $20,000 for a down payment. I'll track progress by my monthly savings rate and total savings. This matters because I want to build equity and have a stable home by January 2025.",
        "refined_goal": "I will save $20,000 for a house down payment by January 2025 through disciplined monthly savings and smart financial planning—because building equity in my own home is crucial for my long-term financial stability and personal comfort.",
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
        print(f"Initial Goal: {data['initial_goal']}")
        print(f"Refinement Response: {data['refinement_response']}")
        print(f"Refined Goal: {data['refined_goal']}")
        print(f"Final Goal: {data['goal']}")
        print("\nAnswers:")
        for question, answer in data['answers'].items():
            print(f"\n{question.replace('_', ' ').title()}:")
            print(answer)
