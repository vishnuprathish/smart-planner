# Smart Goal Planner

A Streamlit app that helps you break down your goals into actionable tasks and daily micro-habits using AI.

## Features

- Enter your goals and get AI-generated clarifying questions
- Get personalized action plans and daily micro-habits
- Store and view your previous goals using Firebase
- Time commitment tracking for each goal

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment:
   - Create a `.streamlit/secrets.toml` file based on `.streamlit/secrets.example.toml`
   - Add your OpenAI API key
   - Add your Firebase service account credentials:
     1. Go to Firebase Console > Project Settings > Service Accounts
     2. Click "Generate New Private Key"
     3. Copy the JSON contents into your `secrets.toml` file following the example format

## Firebase Setup

1. Create a new Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database:
   - Go to Firestore Database in the Firebase Console
   - Click "Create Database"
   - Choose "Start in test mode"
   - Select a location closest to your users
3. Get your service account credentials:
   - Go to Project Settings > Service Accounts
   - Click "Generate New Private Key"
   - Copy the JSON contents into your `secrets.toml` file

## Running the App

```bash
streamlit run src/app.py
```

## Usage

1. Enter your goal in the text input
2. Click "Get Started" to generate clarifying questions
3. Answer the questions and set your daily time commitment
4. Click "Build my plan" to get your personalized action plan
5. View your previous goals in the sidebar

## Security Note

Keep your `secrets.toml` file secure and never commit it to version control. It contains sensitive API keys and credentials.

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
