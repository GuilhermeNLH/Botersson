#!/bin/bash

# Navigate to the repository root
cd "$(dirname "$0")/.."

# Create a Python virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate the venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Load environment variables from .env file if present
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Run the Python application, passing any arguments
python run.py "$@"
