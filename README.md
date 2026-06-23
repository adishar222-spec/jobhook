# Career Assistant

A full-stack AI-powered career assistant to parse resumes, score against ATS, generate cover letters, and auto-apply to jobs using Selenium.

## Setup

1. Create a virtual environment and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in keys (especially Groq API Key).
3. Make sure MongoDB is running locally or provide a URI.
4. Run the application:
   ```bash
   python run.py
   ```
