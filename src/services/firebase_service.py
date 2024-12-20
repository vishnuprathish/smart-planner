import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json
import streamlit as st

class FirebaseService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Firebase service with credentials from streamlit secrets."""
        if not self._initialized:
            try:
                # Create credential dictionary from secrets
                cred_dict = {
                    "type": st.secrets["type"],
                    "project_id": st.secrets["project_id"],
                    "private_key_id": st.secrets["private_key_id"],
                    "private_key": st.secrets["private_key"],
                    "client_email": st.secrets["client_email"],
                    "client_id": st.secrets["client_id"],
                    "auth_uri": st.secrets["auth_uri"],
                    "token_uri": st.secrets["token_uri"],
                    "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
                    "client_x509_cert_url": st.secrets["client_x509_cert_url"],
                    "universe_domain": st.secrets["universe_domain"]
                }
                
                # Initialize Firebase Admin SDK only once
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self._initialized = True
            except Exception as e:
                print(f"Error initializing Firebase: {str(e)}")
                raise

    def store_user_goal(self, goal: str, questions: list, answers: dict, time_commitment: int, tasks: str, habits: str) -> str:
        """Store user's goal and related information in Firestore."""
        try:
            # Create a new document in the goals collection
            doc_ref = self.db.collection('goals').document()
            
            # Store the data
            doc_ref.set({
                'goal': goal,
                'questions': questions,
                'answers': answers,
                'time_commitment': time_commitment,
                'tasks': tasks,
                'habits': habits,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            
            return doc_ref.id
        except Exception as e:
            print(f"Error storing goal in Firebase: {str(e)}")
            return None

    def get_user_goals(self, limit: int = 10) -> list:
        """Retrieve the most recent user goals."""
        try:
            # Query the goals collection, ordered by timestamp
            goals_ref = self.db.collection('goals')
            query = goals_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            
            # Get the documents
            docs = query.stream()
            
            # Convert to list of dictionaries
            goals = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                # Convert timestamp to string for JSON serialization
                if 'timestamp' in data and data['timestamp']:
                    data['timestamp'] = data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                goals.append(data)
            
            return goals
        except Exception as e:
            print(f"Error retrieving goals from Firebase: {str(e)}")
            return []