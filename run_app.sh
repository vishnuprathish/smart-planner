#!/bin/bash

# Activate virtual environment
source venv/bin/activate

case "$1" in
    "test")
        echo "Running in test mode..."
        python -m streamlit run src/Home.py -- --test-mode
        ;;
    *)
        echo "Running in regular mode..."
        python -m streamlit run src/Home.py
        ;;
esac
