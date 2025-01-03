import firebase_admin
from firebase_admin import auth
import streamlit as st
import json
from pyrebase.pyrebase import initialize_app

class UserService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize Firebase Authentication."""
        if not self._initialized:
            try:
                # Initialize Pyrebase with your config
                config = {
                    "apiKey": st.secrets["firebase"]["apiKey"],
                    "authDomain": st.secrets["firebase"]["authDomain"],
                    "projectId": st.secrets["firebase"]["projectId"],
                    "storageBucket": st.secrets["firebase"]["storageBucket"],
                    "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
                    "appId": st.secrets["firebase"]["appId"],
                    "databaseURL": ""  # Add if you're using Realtime Database
                }
                
                self.firebase = initialize_app(config)
                self.auth = self.firebase.auth()
                self._initialized = True
            except Exception as e:
                print(f"Error initializing Firebase Auth: {str(e)}")
                raise

    def sign_up_with_email(self, email, password=None):
        """Sign up a new user with email and password."""
        try:
            # If no password provided, generate a temporary one
            if not password:
                password = self._generate_temp_password()
            
            # Create user in Firebase
            user = self.auth.create_user_with_email_and_password(email, password)
            
            # Send password reset email
            self.auth.send_password_reset_email(email)
            
            # Store user info in session state
            st.session_state.user = {
                'email': email,
                'uid': user['localId'],
                'token': user['idToken']
            }
            
            return True, "Successfully signed up! Check your email to set your password."
        except Exception as e:
            error_message = self._parse_firebase_error(str(e))
            return False, f"Error signing up: {error_message}"

    def sign_in_with_email(self, email, password):
        """Sign in an existing user with email and password."""
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            st.session_state.user = {
                'email': email,
                'uid': user['localId'],
                'token': user['idToken']
            }
            return True, "Successfully signed in!"
        except Exception as e:
            error_message = self._parse_firebase_error(str(e))
            return False, f"Error signing in: {error_message}"

    def sign_out(self):
        """Sign out the current user."""
        if 'user' in st.session_state:
            del st.session_state.user
        return True, "Successfully signed out!"

    def get_current_user(self):
        """Get the current signed-in user."""
        return st.session_state.get('user', None)

    def _generate_temp_password(self):
        """Generate a temporary password for initial signup."""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for i in range(16))

    def _parse_firebase_error(self, error_message):
        """Parse Firebase error messages to user-friendly format."""
        if "EMAIL_EXISTS" in error_message:
            return "Email already exists. Please sign in instead."
        elif "INVALID_EMAIL" in error_message:
            return "Invalid email format."
        elif "WEAK_PASSWORD" in error_message:
            return "Password should be at least 6 characters."
        else:
            return "An error occurred. Please try again."
