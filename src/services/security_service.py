from datetime import datetime, timedelta
import re
from typing import Optional
import streamlit as st

class SecurityService:
    def __init__(self):
        self.max_requests = 50  # Max requests per time window
        self.time_window = 3600  # Time window in seconds (1 hour)
        self._initialize_rate_limits()

    def _initialize_rate_limits(self):
        """Initialize rate limiting in session state"""
        if 'rate_limits' not in st.session_state:
            st.session_state.rate_limits = {}

    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input to prevent prompt injection and other malicious inputs.
        
        Args:
            text: The input text to sanitize
            
        Returns:
            Sanitized text string
        """
        if not isinstance(text, str):
            return ""
            
        # Remove any control characters
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove any potential prompt injection patterns
        patterns = [
            r'system:', r'assistant:', r'user:',  # Role markers
            r'```', r'###',  # Markdown/formatting
            r'<\/?[^>]+>',  # HTML tags
        ]
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
        return text.strip()

    def is_rate_limited(self, session_id: str) -> bool:
        """
        Check if a session has exceeded their rate limit.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            True if session has exceeded rate limit, False otherwise
        """
        now = datetime.now()
        
        # Initialize session's request history if not exists
        if session_id not in st.session_state.rate_limits:
            st.session_state.rate_limits[session_id] = []
            
        # Remove old requests outside the time window
        st.session_state.rate_limits[session_id] = [
            time for time in st.session_state.rate_limits[session_id]
            if now - time < timedelta(seconds=self.time_window)
        ]
        
        # Check if session has exceeded rate limit
        if len(st.session_state.rate_limits[session_id]) >= self.max_requests:
            return True
            
        # Add new request timestamp
        st.session_state.rate_limits[session_id].append(now)
        return False
