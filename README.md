# Smart Goal Planner

A Streamlit-based web application that helps users break down their goals into actionable tasks and daily micro-habits. The app uses OpenAI's GPT-4-mini model to generate personalized plans based on user input and time commitment.

## Features

- Goal input and analysis
- Dynamic question generation based on the goal
- Time commitment customization
- Task breakdown generation
- Conversion of tasks into daily micro-habits
- User-friendly interface with progress indicators

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd windsurf-project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key in one of two ways:

   Option 1: Environment Variable (Recommended for deployment)
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

   Option 2: Secrets file (Good for local development)
   - Copy the example secrets file:
     ```bash
     cp .streamlit/secrets.example.toml .streamlit/secrets.toml
     ```
   - Edit `.streamlit/secrets.toml` with your API key

4. Run the Streamlit app:
```bash
streamlit run src/app.py
```

## Deployment

When deploying to Streamlit Cloud:

1. Fork or clone this repository
2. Add your OpenAI API key to Streamlit Cloud:
   - Go to your app's dashboard on Streamlit Cloud
   - Navigate to "Settings" → "Secrets"
   - Add your API key as `OPENAI_API_KEY`
3. Deploy your app

For other deployment platforms, set the `OPENAI_API_KEY` environment variable in your deployment configuration.

## Usage

1. Open your web browser and navigate to the provided URL (typically http://localhost:8501)

2. Follow the steps in the app:
   - Enter your goal
   - Answer the generated questions
   - Set your daily time commitment
   - Get your personalized plan and micro-habits

## Project Structure

```
windsurf-project/
├── README.md
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── secrets.toml
└── src/
    ├── app.py
    ├── services/
    │   ├── __init__.py
    │   └── openai_service.py
    └── utils/
        ├── __init__.py
        └── constants.py
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Submit a pull request

## License

MIT License
