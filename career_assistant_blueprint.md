# 🎯 Full-Stack AI-Powered Career Assistant — Complete Blueprint

> **Stack:** HTML · CSS · JavaScript · Flask · Python · MongoDB · Groq API · Selenium  
> **Architecture:** Modular MVC · REST API · Responsive UI · Secure Auth

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Project Structure](#3-project-structure)
4. [Database Schema (MongoDB)](#4-database-schema-mongodb)
5. [Backend — Flask Application](#5-backend--flask-application)
6. [Authentication Module](#6-authentication-module)
7. [Resume Module](#7-resume-module)
8. [ATS Scoring Engine](#8-ats-scoring-engine)
9. [Skill-Gap Analysis](#9-skill-gap-analysis)
10. [AI Cover Letter Generator](#10-ai-cover-letter-generator)
11. [Job Recommendations Engine](#11-job-recommendations-engine)
12. [Selenium Auto-Apply Module](#12-selenium-auto-apply-module)
13. [Application Tracker Dashboard](#13-application-tracker-dashboard)
14. [Frontend — HTML/CSS/JavaScript](#14-frontend--htmlcssjavascript)
15. [Groq API Integration](#15-groq-api-integration)
16. [Environment & Configuration](#16-environment--configuration)
17. [Installation & Setup](#17-installation--setup)
18. [API Endpoints Reference](#18-api-endpoints-reference)
19. [Security Considerations](#19-security-considerations)
20. [Deployment Guide](#20-deployment-guide)

---

## 1. Project Overview

The Career Assistant is a full-stack web application that uses AI (via Groq's ultra-fast LLM API) to help job seekers optimize their resumes, identify skill gaps, generate cover letters, discover matching jobs, and semi-automatically apply — all from a single responsive dashboard.

### Core Features

| Feature | Description |
|---|---|
| **Auth System** | JWT-based register/login with bcrypt password hashing |
| **Resume Manager** | Upload PDF/DOCX or build resume via guided form |
| **ATS Scorer** | Keyword-matching score against job descriptions |
| **Skill-Gap Analysis** | Compare resume skills vs. target role requirements |
| **AI Suggestions** | Groq LLM-powered resume improvement recommendations |
| **Cover Letter AI** | Personalized, role-specific cover letters via Groq |
| **Job Recommendations** | Role-matched jobs scraped or fetched via API |
| **Application Tracker** | Kanban-style dashboard to track all job applications |
| **Selenium Auto-Apply** | Semi-automatic form fill with user confirmation gate |

---

## 2. System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     BROWSER (Client)                     │
│         HTML · CSS (Custom + Tailwind) · Vanilla JS      │
└──────────────────┬───────────────────────────────────────┘
                   │ HTTP / REST
┌──────────────────▼───────────────────────────────────────┐
│               FLASK APPLICATION SERVER                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │   Auth   │ │  Resume  │ │   ATS    │ │    Jobs    │  │
│  │ Blueprint│ │ Blueprint│ │ Blueprint│ │  Blueprint │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────────┐  │
│  │  Cover   │ │Tracker   │ │    Selenium Auto-Apply   │  │
│  │  Letter  │ │Dashboard │ │       Blueprint          │  │
│  └──────────┘ └──────────┘ └──────────────────────────┘  │
└───────────┬─────────────────────────┬────────────────────┘
            │                         │
┌───────────▼──────────┐   ┌──────────▼──────────────────┐
│  MongoDB (PyMongo)   │   │  External Services          │
│  ┌────────────────┐  │   │  ┌────────────────────────┐  │
│  │  users         │  │   │  │  Groq API (LLM)        │  │
│  │  resumes       │  │   │  │  - Resume analysis     │  │
│  │  applications  │  │   │  │  - Cover letter gen    │  │
│  │  jobs          │  │   │  │  - Skill gap analysis  │  │
│  │  cover_letters │  │   │  └────────────────────────┘  │
│  └────────────────┘  │   │  ┌────────────────────────┐  │
└──────────────────────┘   │  │  Selenium WebDriver    │  │
                           │  │  - ChromeDriver        │  │
                           │  │  - Job site auto-fill  │  │
                           │  └────────────────────────┘  │
                           └─────────────────────────────┘
```

---

## 3. Project Structure

```
career_assistant/
│
├── app/
│   ├── __init__.py                  # Flask app factory
│   ├── config.py                    # Config classes (Dev/Prod/Test)
│   ├── extensions.py                # PyMongo, JWT, CORS init
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py                # /register, /login, /logout, /refresh
│   │   ├── models.py                # User schema + methods
│   │   └── utils.py                 # JWT helpers, decorators
│   │
│   ├── resume/
│   │   ├── __init__.py
│   │   ├── routes.py                # /upload, /create, /get, /delete
│   │   ├── parser.py                # PDF/DOCX text extraction
│   │   ├── builder.py               # Form-based resume builder
│   │   └── models.py                # Resume schema
│   │
│   ├── ats/
│   │   ├── __init__.py
│   │   ├── routes.py                # /score, /analyze
│   │   ├── scorer.py                # ATS keyword scoring logic
│   │   └── skill_gap.py             # Skill comparison engine
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── groq_client.py           # Groq API wrapper
│   │   ├── cover_letter.py          # Cover letter generation
│   │   ├── suggestions.py           # Resume improvement AI
│   │   └── prompts.py               # All LLM prompt templates
│   │
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── routes.py                # /recommend, /search, /save
│   │   ├── recommender.py           # Role-based job matching
│   │   └── models.py                # Job schema
│   │
│   ├── tracker/
│   │   ├── __init__.py
│   │   ├── routes.py                # /applications CRUD
│   │   └── models.py                # Application schema
│   │
│   ├── selenium_apply/
│   │   ├── __init__.py
│   │   ├── routes.py                # /auto-apply, /confirm, /status
│   │   ├── driver.py                # WebDriver setup & management
│   │   ├── form_filler.py           # Generic form-fill strategies
│   │   └── sites/
│   │       ├── linkedin.py          # LinkedIn-specific automation
│   │       ├── indeed.py            # Indeed-specific automation
│   │       └── greenhouse.py        # Greenhouse ATS automation
│   │
│   └── static/
│       ├── css/
│       │   ├── main.css             # Global styles + CSS variables
│       │   ├── auth.css             # Login/register pages
│       │   ├── dashboard.css        # Dashboard layout
│       │   ├── resume.css           # Resume builder/viewer
│       │   └── tracker.css          # Kanban tracker board
│       ├── js/
│       │   ├── api.js               # Centralized API fetch wrapper
│       │   ├── auth.js              # Auth flow (login/register/logout)
│       │   ├── resume.js            # Resume upload & builder UI
│       │   ├── ats.js               # ATS score display & analysis
│       │   ├── jobs.js              # Job cards & recommendations
│       │   ├── cover_letter.js      # Cover letter generation UI
│       │   ├── tracker.js           # Kanban board interactions
│       │   └── apply.js             # Auto-apply confirmation flow
│       └── img/
│           └── logo.svg
│
├── templates/
│   ├── base.html                    # Base layout with navbar/sidebar
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/
│   │   └── index.html               # Main dashboard
│   ├── resume/
│   │   ├── upload.html
│   │   └── builder.html
│   ├── ats/
│   │   └── results.html
│   ├── jobs/
│   │   └── recommendations.html
│   ├── cover_letter/
│   │   └── editor.html
│   └── tracker/
│       └── board.html
│
├── tests/
│   ├── test_auth.py
│   ├── test_ats.py
│   ├── test_ai.py
│   └── test_selenium.py
│
├── scripts/
│   └── seed_jobs.py                 # Seed sample job data
│
├── uploads/                         # Temporary resume file storage
├── .env                             # Environment variables (never commit)
├── .env.example                     # Template for .env
├── requirements.txt
├── run.py                           # Entry point
└── README.md
```

---

## 4. Database Schema (MongoDB)

### Collection: `users`

```python
{
    "_id": ObjectId(),
    "name": "Jane Smith",
    "email": "jane@example.com",
    "password_hash": "$2b$12$...",       # bcrypt hash
    "created_at": datetime,
    "updated_at": datetime,
    "profile": {
        "target_role": "Data Scientist",
        "target_industry": "Tech",
        "location": "Remote",
        "experience_years": 3
    },
    "active_resume_id": ObjectId()        # Reference to resumes collection
}
```

### Collection: `resumes`

```python
{
    "_id": ObjectId(),
    "user_id": ObjectId(),                # Reference to users
    "file_name": "jane_resume.pdf",
    "raw_text": "Jane Smith | Data Scientist...",
    "parsed": {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "+1-555-0100",
        "summary": "...",
        "skills": ["Python", "TensorFlow", "SQL", "Docker"],
        "experience": [
            {
                "company": "Acme Corp",
                "title": "ML Engineer",
                "start": "2021-06",
                "end": "2023-12",
                "bullets": ["Built recommendation system...", "..."]
            }
        ],
        "education": [
            {
                "school": "MIT",
                "degree": "B.Sc. Computer Science",
                "year": 2021
            }
        ],
        "certifications": ["AWS Certified ML Specialty"]
    },
    "ats_scores": [                        # History of ATS checks
        {
            "job_description": "...",
            "score": 78,
            "matched_keywords": ["Python", "SQL"],
            "missing_keywords": ["Spark", "Kafka"],
            "checked_at": datetime
        }
    ],
    "created_at": datetime,
    "updated_at": datetime
}
```

### Collection: `cover_letters`

```python
{
    "_id": ObjectId(),
    "user_id": ObjectId(),
    "resume_id": ObjectId(),
    "job_id": ObjectId(),                  # Optional: linked job
    "company": "Google",
    "role": "Senior Data Scientist",
    "content": "Dear Hiring Manager, ...",
    "version": 1,
    "created_at": datetime
}
```

### Collection: `jobs`

```python
{
    "_id": ObjectId(),
    "title": "Senior Data Scientist",
    "company": "Google",
    "location": "Remote / Mountain View, CA",
    "description": "We are looking for...",
    "required_skills": ["Python", "TensorFlow", "BigQuery"],
    "experience_level": "Senior",
    "job_type": "Full-time",
    "apply_url": "https://careers.google.com/...",
    "source": "LinkedIn",                  # Where job was found
    "posted_at": datetime,
    "scraped_at": datetime,
    "is_active": True
}
```

### Collection: `applications`

```python
{
    "_id": ObjectId(),
    "user_id": ObjectId(),
    "job_id": ObjectId(),
    "resume_id": ObjectId(),
    "cover_letter_id": ObjectId(),
    "status": "applied",                   # "saved" | "applied" | "interview" | "offer" | "rejected"
    "ats_score": 82,
    "applied_at": datetime,
    "notes": "Referral from John",
    "next_follow_up": datetime,
    "selenium_session": {                  # Metadata from auto-apply
        "attempted": True,
        "success": True,
        "confirmation_number": "APP-123456",
        "screenshot_path": "/uploads/screenshots/app_123.png",
        "applied_at": datetime
    },
    "timeline": [
        {"status": "saved", "at": datetime},
        {"status": "applied", "at": datetime}
    ],
    "updated_at": datetime
}
```

---

## 5. Backend — Flask Application

### `app/__init__.py` — App Factory

```python
from flask import Flask
from .config import config_by_name
from .extensions import mongo, jwt, cors
from .auth.routes import auth_bp
from .resume.routes import resume_bp
from .ats.routes import ats_bp
from .ai.cover_letter import cover_letter_bp
from .jobs.routes import jobs_bp
from .tracker.routes import tracker_bp
from .selenium_apply.routes import apply_bp


def create_app(config_name="development"):
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    mongo.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(resume_bp, url_prefix="/api/resume")
    app.register_blueprint(ats_bp, url_prefix="/api/ats")
    app.register_blueprint(cover_letter_bp, url_prefix="/api/cover-letter")
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(tracker_bp, url_prefix="/api/tracker")
    app.register_blueprint(apply_bp, url_prefix="/api/apply")

    return app
```

### `app/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-change-me")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/career_assistant")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload
    ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama3-70b-8192"
    JWT_ACCESS_TOKEN_EXPIRES = 3600       # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 86400 * 7 # 7 days


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    MONGO_URI = "mongodb://localhost:27017/career_assistant_test"


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
```

### `run.py`

```python
from app import create_app
import os

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
```

---

## 6. Authentication Module

### `app/auth/routes.py`

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from .models import UserModel
from ..extensions import mongo
import bcrypt

auth_bp = Blueprint("auth", __name__)
users = UserModel()


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    required = ["name", "email", "password"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    if users.find_by_email(data["email"]):
        return jsonify({"error": "Email already registered"}), 409

    user_id = users.create(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        target_role=data.get("target_role", "")
    )

    access_token = create_access_token(identity=str(user_id))
    refresh_token = create_refresh_token(identity=str(user_id))

    return jsonify({
        "message": "Registration successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": str(user_id)
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = users.find_by_email(data.get("email"))

    if not user or not bcrypt.checkpw(
        data["password"].encode(), user["password_hash"].encode()
    ):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user["_id"]))
    refresh_token = create_refresh_token(identity=str(user["_id"]))

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "target_role": user.get("profile", {}).get("target_role", "")
        }
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = users.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user["_id"] = str(user["_id"])
    user.pop("password_hash", None)
    return jsonify(user), 200
```

### `app/auth/models.py`

```python
from ..extensions import mongo
from bson import ObjectId
from datetime import datetime
import bcrypt


class UserModel:
    @property
    def collection(self):
        return mongo.db.users

    def create(self, name, email, password, target_role=""):
        password_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()
        user = {
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "profile": {
                "target_role": target_role,
                "target_industry": "",
                "location": "",
                "experience_years": 0
            },
            "active_resume_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = self.collection.insert_one(user)
        return result.inserted_id

    def find_by_email(self, email):
        return self.collection.find_one({"email": email})

    def find_by_id(self, user_id):
        return self.collection.find_one({"_id": ObjectId(user_id)})

    def update_profile(self, user_id, profile_data):
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile": profile_data, "updated_at": datetime.utcnow()}}
        )
```

---

## 7. Resume Module

### `app/resume/parser.py`

```python
import pdfplumber
from docx import Document as DocxDocument
import re
import os


def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract raw text from DOCX."""
    doc = DocxDocument(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_resume_text(file_path: str) -> str:
    """Route extraction based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    raise ValueError(f"Unsupported file type: {ext}")


def extract_email(text: str) -> str:
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    match = re.search(
        r"(\+?\d{1,3}[\s\-]?)?(\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})", text
    )
    return match.group(0).strip() if match else ""


def extract_skills_basic(text: str, skill_list: list) -> list:
    """Simple keyword match against a known skill vocabulary."""
    text_lower = text.lower()
    return [skill for skill in skill_list if skill.lower() in text_lower]
```

### `app/resume/routes.py`

```python
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from .parser import extract_resume_text, extract_email, extract_phone
from .models import ResumeModel
from ..ai.groq_client import GroqClient
import os

resume_bp = Blueprint("resume", __name__)
resume_model = ResumeModel()
groq = GroqClient()

ALLOWED = {"pdf", "docx", "doc"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED


@resume_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_resume():
    user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use PDF or DOCX"}), 400

    filename = secure_filename(file.filename)
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(upload_path)

    # Extract text
    raw_text = extract_resume_text(upload_path)

    # AI-assisted parsing: ask Groq to return structured JSON
    parsed = groq.parse_resume(raw_text)

    resume_id = resume_model.create(
        user_id=user_id,
        file_name=filename,
        raw_text=raw_text,
        parsed=parsed
    )

    os.remove(upload_path)  # Clean up temp file

    return jsonify({
        "message": "Resume uploaded successfully",
        "resume_id": str(resume_id),
        "parsed": parsed
    }), 201


@resume_bp.route("/", methods=["GET"])
@jwt_required()
def get_resumes():
    user_id = get_jwt_identity()
    resumes = resume_model.get_by_user(user_id)
    return jsonify(resumes), 200


@resume_bp.route("/<resume_id>", methods=["DELETE"])
@jwt_required()
def delete_resume(resume_id):
    user_id = get_jwt_identity()
    resume_model.delete(resume_id, user_id)
    return jsonify({"message": "Resume deleted"}), 200
```

---

## 8. ATS Scoring Engine

### `app/ats/scorer.py`

```python
import re
from collections import Counter
from typing import Tuple


COMMON_STOP_WORDS = {
    "the", "and", "for", "with", "you", "are", "our", "this",
    "will", "have", "your", "that", "from", "all", "can", "more"
}


def tokenize(text: str) -> set:
    """Lowercase, remove punctuation, split into unique meaningful words."""
    words = re.findall(r"\b[a-zA-Z][a-zA-Z+#\.]{1,}\b", text.lower())
    return set(w for w in words if w not in COMMON_STOP_WORDS)


def extract_keywords(jd_text: str, top_n: int = 40) -> list:
    """
    Frequency-rank keywords from a job description.
    Returns top N meaningful keywords.
    """
    words = re.findall(r"\b[a-zA-Z][a-zA-Z+#\.]{1,}\b", jd_text.lower())
    filtered = [w for w in words if w not in COMMON_STOP_WORDS]
    freq = Counter(filtered)
    return [word for word, _ in freq.most_common(top_n)]


def calculate_ats_score(resume_text: str, jd_text: str) -> dict:
    """
    Calculate ATS compatibility score.

    Returns:
        score (int): 0–100 percentage match
        matched_keywords (list): Keywords present in both
        missing_keywords (list): Important JD keywords absent from resume
        breakdown (dict): Section-level scoring
    """
    resume_tokens = tokenize(resume_text)
    jd_keywords = extract_keywords(jd_text, top_n=50)

    matched = [kw for kw in jd_keywords if kw in resume_tokens]
    missing = [kw for kw in jd_keywords if kw not in resume_tokens]

    score = round(len(matched) / max(len(jd_keywords), 1) * 100)

    return {
        "score": score,
        "total_keywords_checked": len(jd_keywords),
        "matched_keywords": matched,
        "missing_keywords": missing[:20],  # Top 20 missing
        "rating": _rating_label(score)
    }


def _rating_label(score: int) -> str:
    if score >= 80:
        return "Excellent"
    elif score >= 65:
        return "Good"
    elif score >= 50:
        return "Fair"
    else:
        return "Needs Work"
```

### `app/ats/routes.py`

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .scorer import calculate_ats_score
from .skill_gap import analyze_skill_gap
from ..resume.models import ResumeModel
from ..ai.groq_client import GroqClient

ats_bp = Blueprint("ats", __name__)
resume_model = ResumeModel()
groq = GroqClient()


@ats_bp.route("/score", methods=["POST"])
@jwt_required()
def score():
    user_id = get_jwt_identity()
    data = request.get_json()

    resume_id = data.get("resume_id")
    jd_text = data.get("job_description", "")

    if not resume_id or not jd_text:
        return jsonify({"error": "resume_id and job_description are required"}), 400

    resume = resume_model.get_by_id(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    # ATS Score
    ats_result = calculate_ats_score(resume["raw_text"], jd_text)

    # Skill Gap
    target_skills = data.get("target_skills", [])
    resume_skills = resume.get("parsed", {}).get("skills", [])
    gap_result = analyze_skill_gap(resume_skills, jd_text, target_skills)

    # AI improvement suggestions
    suggestions = groq.get_resume_suggestions(
        resume_text=resume["raw_text"],
        jd_text=jd_text,
        missing_keywords=ats_result["missing_keywords"]
    )

    # Save ATS history to resume
    resume_model.add_ats_score(resume_id, {
        "job_description": jd_text[:500],
        "score": ats_result["score"],
        "matched_keywords": ats_result["matched_keywords"],
        "missing_keywords": ats_result["missing_keywords"]
    })

    return jsonify({
        "ats": ats_result,
        "skill_gap": gap_result,
        "suggestions": suggestions
    }), 200
```

---

## 9. Skill-Gap Analysis

### `app/ats/skill_gap.py`

```python
import re

# Curated tech skill vocabulary (extend as needed)
TECH_SKILLS_VOCAB = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust",
    "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "Redis",
    "React", "Vue", "Angular", "Next.js", "Node.js", "Flask", "Django", "FastAPI",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform",
    "Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch", "scikit-learn",
    "Spark", "Kafka", "Airflow", "Hadoop", "dbt", "Tableau", "Power BI",
    "Git", "CI/CD", "Jenkins", "GitHub Actions", "Linux", "REST API", "GraphQL"
]


def extract_skills_from_text(text: str, vocab: list = TECH_SKILLS_VOCAB) -> list:
    """Case-insensitive match of known skills in text."""
    text_lower = text.lower()
    return [skill for skill in vocab if skill.lower() in text_lower]


def analyze_skill_gap(
    resume_skills: list,
    jd_text: str,
    target_skills: list = None
) -> dict:
    """
    Compare resume skills against job description and optional target list.

    Returns:
        matched: Skills user already has that are required
        missing: Skills required but absent from resume
        recommended_learning: Top 5 skills to learn with priority score
    """
    jd_skills = extract_skills_from_text(jd_text)
    if target_skills:
        jd_skills = list(set(jd_skills + target_skills))

    resume_skills_lower = [s.lower() for s in resume_skills]

    matched = [s for s in jd_skills if s.lower() in resume_skills_lower]
    missing = [s for s in jd_skills if s.lower() not in resume_skills_lower]

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": round(
            len(matched) / max(len(jd_skills), 1) * 100
        ),
        "recommended_learning": missing[:5]  # Prioritize first 5 gaps
    }
```

---

## 10. AI Cover Letter Generator

### `app/ai/prompts.py`

```python
RESUME_PARSE_PROMPT = """
You are a resume parser. Extract structured information from the resume text below.
Return ONLY a valid JSON object with these exact keys:
{
  "name": "",
  "email": "",
  "phone": "",
  "summary": "",
  "skills": [],
  "experience": [{"company": "", "title": "", "start": "", "end": "", "bullets": []}],
  "education": [{"school": "", "degree": "", "year": ""}],
  "certifications": []
}

Resume Text:
{resume_text}
"""

RESUME_SUGGESTIONS_PROMPT = """
You are an expert resume consultant and ATS optimization specialist.

The candidate's resume scored {score}% against the job description below.
Missing keywords: {missing_keywords}

Your task:
1. List 5 specific, actionable bullet-point improvements to the resume
2. Suggest how to naturally incorporate the missing keywords
3. Identify any weak language and suggest stronger alternatives

Job Description:
{jd_text}

Resume Text:
{resume_text}

Return a structured JSON:
{{
  "improvements": [],
  "keyword_suggestions": [],
  "language_upgrades": []
}}
"""

COVER_LETTER_PROMPT = """
You are a professional cover letter writer. Write a compelling, personalized
cover letter for the following applicant targeting the role described below.

Guidelines:
- 3–4 paragraphs, professional but personable
- Opening: Strong hook referencing the specific role and company
- Body: Connect candidate's top 3 achievements to the role requirements
- Closing: Confident call-to-action
- Do NOT use generic filler phrases like "I am writing to apply for..."

Applicant Info:
Name: {name}
Target Role: {role}
Company: {company}
Top Skills: {skills}
Key Achievements: {achievements}

Job Description:
{jd_text}

Return ONLY the cover letter text, no additional commentary.
"""

SKILL_GAP_ADVICE_PROMPT = """
The candidate wants to become a {target_role}.
They have these skills: {current_skills}
They are missing these required skills: {missing_skills}

Provide a concise learning roadmap:
1. Rank the missing skills by importance for the target role
2. For each top 3 skill, suggest one free resource to learn it
3. Estimate weeks to reach job-ready proficiency

Return as JSON:
{{
  "prioritized_skills": [],
  "learning_resources": {{}},
  "timeline_weeks": {{}}
}}
"""
```

### `app/ai/groq_client.py`

```python
from groq import Groq
import json
from flask import current_app
from .prompts import (
    RESUME_PARSE_PROMPT,
    RESUME_SUGGESTIONS_PROMPT,
    COVER_LETTER_PROMPT,
    SKILL_GAP_ADVICE_PROMPT
)


class GroqClient:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = Groq(api_key=current_app.config["GROQ_API_KEY"])
        return self._client

    def _chat(self, prompt: str, system: str = "You are a helpful assistant.",
              max_tokens: int = 2000, temperature: float = 0.3) -> str:
        response = self.client.chat.completions.create(
            model=current_app.config["GROQ_MODEL"],
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()

    def parse_resume(self, resume_text: str) -> dict:
        prompt = RESUME_PARSE_PROMPT.format(resume_text=resume_text[:4000])
        raw = self._chat(prompt, system="You are a precise JSON extractor.")
        try:
            # Strip any markdown code fences if present
            raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"error": "Failed to parse resume", "raw": raw}

    def get_resume_suggestions(self, resume_text: str, jd_text: str,
                                missing_keywords: list, score: int = 0) -> dict:
        prompt = RESUME_SUGGESTIONS_PROMPT.format(
            resume_text=resume_text[:3000],
            jd_text=jd_text[:2000],
            missing_keywords=", ".join(missing_keywords),
            score=score
        )
        raw = self._chat(prompt)
        try:
            raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"improvements": [], "keyword_suggestions": [], "language_upgrades": []}

    def generate_cover_letter(self, name: str, role: str, company: str,
                               skills: list, achievements: list, jd_text: str) -> str:
        prompt = COVER_LETTER_PROMPT.format(
            name=name,
            role=role,
            company=company,
            skills=", ".join(skills[:8]),
            achievements="\n".join(f"- {a}" for a in achievements[:5]),
            jd_text=jd_text[:2000]
        )
        return self._chat(prompt, temperature=0.6, max_tokens=800)

    def get_skill_gap_advice(self, target_role: str,
                              current_skills: list, missing_skills: list) -> dict:
        prompt = SKILL_GAP_ADVICE_PROMPT.format(
            target_role=target_role,
            current_skills=", ".join(current_skills),
            missing_skills=", ".join(missing_skills[:10])
        )
        raw = self._chat(prompt)
        try:
            raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}
```

### `app/ai/cover_letter.py` (routes)

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .groq_client import GroqClient
from ..resume.models import ResumeModel
from ..extensions import mongo
from bson import ObjectId
from datetime import datetime

cover_letter_bp = Blueprint("cover_letter", __name__)
groq = GroqClient()
resume_model = ResumeModel()


@cover_letter_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate():
    user_id = get_jwt_identity()
    data = request.get_json()

    resume_id = data.get("resume_id")
    resume = resume_model.get_by_id(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404

    parsed = resume.get("parsed", {})
    achievements = [
        bullet
        for exp in parsed.get("experience", [])
        for bullet in exp.get("bullets", [])[:2]
    ]

    letter_text = groq.generate_cover_letter(
        name=parsed.get("name", ""),
        role=data.get("role", ""),
        company=data.get("company", ""),
        skills=parsed.get("skills", []),
        achievements=achievements,
        jd_text=data.get("job_description", "")
    )

    # Save to DB
    doc = {
        "user_id": ObjectId(user_id),
        "resume_id": ObjectId(resume_id),
        "company": data.get("company", ""),
        "role": data.get("role", ""),
        "content": letter_text,
        "version": 1,
        "created_at": datetime.utcnow()
    }
    result = mongo.db.cover_letters.insert_one(doc)

    return jsonify({
        "cover_letter_id": str(result.inserted_id),
        "content": letter_text
    }), 201


@cover_letter_bp.route("/", methods=["GET"])
@jwt_required()
def list_cover_letters():
    user_id = get_jwt_identity()
    letters = list(mongo.db.cover_letters.find({"user_id": ObjectId(user_id)}))
    for l in letters:
        l["_id"] = str(l["_id"])
        l["user_id"] = str(l["user_id"])
        l["resume_id"] = str(l["resume_id"])
    return jsonify(letters), 200
```

---

## 11. Job Recommendations Engine

### `app/jobs/recommender.py`

```python
from ..extensions import mongo
from bson import ObjectId
import re


def score_job_match(resume_skills: list, job: dict) -> int:
    """Simple skill overlap score between resume and job required skills."""
    required = [s.lower() for s in job.get("required_skills", [])]
    candidate = [s.lower() for s in resume_skills]
    if not required:
        return 0
    overlap = len(set(required) & set(candidate))
    return round(overlap / len(required) * 100)


def get_recommendations(user_id: str, resume_id: str, limit: int = 10) -> list:
    """
    Return top job recommendations for a user based on:
    1. Target role match in job title
    2. Skill overlap with resume
    """
    from ..resume.models import ResumeModel
    from ..auth.models import UserModel

    user = UserModel().find_by_id(user_id)
    resume = ResumeModel().get_by_id(resume_id)

    target_role = user.get("profile", {}).get("target_role", "")
    resume_skills = resume.get("parsed", {}).get("skills", []) if resume else []

    # Keyword-based title filter
    title_regex = re.compile("|".join(target_role.split()), re.IGNORECASE) \
        if target_role else re.compile(".*")

    jobs = list(mongo.db.jobs.find({
        "title": {"$regex": title_regex},
        "is_active": True
    }).limit(limit * 3))

    # Score and sort
    scored = [
        {**job, "match_score": score_job_match(resume_skills, job)}
        for job in jobs
    ]
    scored.sort(key=lambda x: x["match_score"], reverse=True)

    # Serialize
    for j in scored:
        j["_id"] = str(j["_id"])

    return scored[:limit]
```

---

## 12. Selenium Auto-Apply Module

### `app/selenium_apply/driver.py`

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os


def get_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Initialize and return a Chrome WebDriver.
    Set headless=True for background automation,
    False for visible user-confirmation mode.
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Anti-bot detection countermeasure
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def take_screenshot(driver: webdriver.Chrome, path: str) -> str:
    """Save a screenshot and return the path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    driver.save_screenshot(path)
    return path
```

### `app/selenium_apply/form_filler.py`

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


class FormFiller:
    def __init__(self, driver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def fill_text(self, selector: str, value: str,
                   by: By = By.CSS_SELECTOR) -> bool:
        try:
            el = self.wait.until(EC.presence_of_element_located((by, selector)))
            el.clear()
            el.send_keys(value)
            return True
        except TimeoutException:
            return False

    def click(self, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        try:
            el = self.wait.until(EC.element_to_be_clickable((by, selector)))
            el.click()
            return True
        except TimeoutException:
            return False

    def select_dropdown(self, selector: str, value: str,
                         by: By = By.CSS_SELECTOR) -> bool:
        try:
            el = self.wait.until(EC.presence_of_element_located((by, selector)))
            Select(el).select_by_visible_text(value)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def upload_file(self, input_selector: str, file_path: str) -> bool:
        try:
            el = self.driver.find_element(By.CSS_SELECTOR, input_selector)
            el.send_keys(file_path)
            return True
        except NoSuchElementException:
            return False

    def wait_for_confirmation(self, selector: str,
                               timeout: int = 30) -> bool:
        """Wait for a success confirmation element on the page."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except TimeoutException:
            return False
```

### `app/selenium_apply/sites/linkedin.py`

```python
from selenium.webdriver.common.by import By
from ..form_filler import FormFiller
from ..driver import take_screenshot
import time


class LinkedInApplier:
    """
    Handles Easy Apply flow on LinkedIn.
    NOTE: Requires user to be pre-logged in via browser session
    or pass session cookies.
    """
    EASY_APPLY_BTN = "button.jobs-apply-button"
    PHONE_INPUT = "input[id*='phoneNumber']"
    SUBMIT_BTN = "button[aria-label='Submit application']"
    NEXT_BTN = "button[aria-label='Continue to next step']"
    SUCCESS_ELEMENT = ".artdeco-inline-feedback--success"

    def __init__(self, driver):
        self.driver = driver
        self.filler = FormFiller(driver)

    def apply(self, job_url: str, applicant_data: dict,
               resume_path: str, screenshot_dir: str) -> dict:
        """
        Semi-automatic LinkedIn Easy Apply.
        Returns result dict with success status and screenshot path.
        """
        self.driver.get(job_url)
        time.sleep(2)

        # Click Easy Apply
        if not self.filler.click(self.EASY_APPLY_BTN):
            return {"success": False, "error": "Easy Apply button not found"}

        time.sleep(1)

        # Fill phone if prompted
        self.filler.fill_text(
            self.PHONE_INPUT, applicant_data.get("phone", "")
        )

        # Upload resume if file input present
        self.filler.upload_file(
            "input[name='resume']", resume_path
        )

        # Step through multi-step form
        for _ in range(5):  # Max 5 steps
            if not self.filler.click(self.NEXT_BTN):
                break
            time.sleep(1.5)

        # Submit
        self.filler.click(self.SUBMIT_BTN)
        time.sleep(2)

        # Take screenshot as proof
        screenshot_path = f"{screenshot_dir}/linkedin_{int(time.time())}.png"
        take_screenshot(self.driver, screenshot_path)

        success = self.filler.wait_for_confirmation(self.SUCCESS_ELEMENT, timeout=10)

        return {
            "success": success,
            "screenshot_path": screenshot_path,
            "platform": "LinkedIn"
        }
```

### `app/selenium_apply/routes.py`

```python
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .driver import get_driver
from .sites.linkedin import LinkedInApplier
from ..tracker.models import ApplicationModel
from bson import ObjectId
import threading
import os

apply_bp = Blueprint("apply", __name__)
app_model = ApplicationModel()

# Thread-local driver storage (one session per user ideally)
_sessions = {}


@apply_bp.route("/prepare", methods=["POST"])
@jwt_required()
def prepare_application():
    """
    Prepare application data and show preview to user
    before triggering Selenium.
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    return jsonify({
        "preview": {
            "job_url": data.get("job_url"),
            "platform": data.get("platform", "LinkedIn"),
            "resume_name": data.get("resume_name"),
            "cover_letter_preview": data.get("cover_letter_text", "")[:300] + "...",
        },
        "message": "Please review the details above and confirm to proceed."
    }), 200


@apply_bp.route("/confirm", methods=["POST"])
@jwt_required()
def confirm_apply():
    """
    User has confirmed — trigger Selenium auto-apply in background thread.
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    job_url = data.get("job_url")
    resume_path = data.get("resume_path")
    platform = data.get("platform", "linkedin")
    application_id = data.get("application_id")

    applicant_data = {
        "phone": data.get("phone", ""),
        "name": data.get("name", ""),
        "email": data.get("email", "")
    }

    screenshot_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "screenshots")

    def run_apply():
        driver = get_driver(headless=False)
        try:
            if platform == "linkedin":
                applier = LinkedInApplier(driver)
                result = applier.apply(job_url, applicant_data, resume_path, screenshot_dir)
            else:
                result = {"success": False, "error": f"Platform '{platform}' not yet supported"}

            # Update application tracker
            if application_id:
                app_model.update_selenium_result(application_id, result)
        finally:
            driver.quit()

    thread = threading.Thread(target=run_apply, daemon=True)
    thread.start()

    return jsonify({
        "message": "Application submission started. Check your tracker for results.",
        "application_id": application_id
    }), 202
```

---

## 13. Application Tracker Dashboard

### `app/tracker/models.py`

```python
from ..extensions import mongo
from bson import ObjectId
from datetime import datetime


class ApplicationModel:
    @property
    def col(self):
        return mongo.db.applications

    def create(self, user_id, job_id, resume_id, cover_letter_id=None,
               ats_score=0, notes="") -> str:
        doc = {
            "user_id": ObjectId(user_id),
            "job_id": ObjectId(job_id),
            "resume_id": ObjectId(resume_id),
            "cover_letter_id": ObjectId(cover_letter_id) if cover_letter_id else None,
            "status": "saved",
            "ats_score": ats_score,
            "notes": notes,
            "applied_at": None,
            "next_follow_up": None,
            "selenium_session": {},
            "timeline": [{"status": "saved", "at": datetime.utcnow()}],
            "updated_at": datetime.utcnow()
        }
        result = self.col.insert_one(doc)
        return str(result.inserted_id)

    def update_status(self, app_id: str, status: str):
        self.col.update_one(
            {"_id": ObjectId(app_id)},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                },
                "$push": {
                    "timeline": {"status": status, "at": datetime.utcnow()}
                }
            }
        )

    def update_selenium_result(self, app_id: str, result: dict):
        update = {
            "selenium_session": {
                **result,
                "attempted": True,
                "applied_at": datetime.utcnow()
            },
            "updated_at": datetime.utcnow()
        }
        if result.get("success"):
            update["status"] = "applied"
            update["applied_at"] = datetime.utcnow()
        self.col.update_one({"_id": ObjectId(app_id)}, {"$set": update})

    def get_by_user(self, user_id: str) -> list:
        apps = list(self.col.find({"user_id": ObjectId(user_id)}).sort("updated_at", -1))
        for a in apps:
            a["_id"] = str(a["_id"])
            a["user_id"] = str(a["user_id"])
            a["job_id"] = str(a["job_id"])
            a["resume_id"] = str(a["resume_id"])
        return apps
```

---

## 14. Frontend — HTML/CSS/JavaScript

### `templates/base.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}Career Assistant{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}" />
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar">
        <a href="/" class="nav-brand">🎯 CareerAI</a>
        <div class="nav-links" id="nav-links">
            <a href="/dashboard">Dashboard</a>
            <a href="/resume">Resume</a>
            <a href="/jobs">Jobs</a>
            <a href="/tracker">Tracker</a>
            <button id="logout-btn" class="btn btn-outline" onclick="logout()">Logout</button>
        </div>
        <button class="hamburger" id="hamburger">☰</button>
    </nav>

    <main class="main-content">
        {% block content %}{% endblock %}
    </main>

    <script src="{{ url_for('static', filename='js/api.js') }}"></script>
    <script src="{{ url_for('static', filename='js/auth.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### `static/css/main.css`

```css
/* =============================================
   CSS Custom Properties (Design Tokens)
   ============================================= */
:root {
    --primary: #4f46e5;
    --primary-hover: #4338ca;
    --primary-light: #eef2ff;
    --secondary: #06b6d4;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-600: #4b5563;
    --gray-800: #1f2937;
    --gray-900: #111827;
    --white: #ffffff;
    --radius: 0.75rem;
    --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.07);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --transition: 0.2s ease;
}

/* Reset */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: var(--font); color: var(--gray-800); background: var(--gray-50); }

/* Navbar */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2rem;
    background: var(--white);
    border-bottom: 1px solid var(--gray-200);
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: var(--shadow);
}
.nav-brand { font-size: 1.3rem; font-weight: 700; color: var(--primary); text-decoration: none; }
.nav-links { display: flex; align-items: center; gap: 1.5rem; }
.nav-links a { color: var(--gray-600); text-decoration: none; font-size: 0.9rem;
    transition: color var(--transition); }
.nav-links a:hover { color: var(--primary); }
.hamburger { display: none; background: none; border: none; font-size: 1.5rem; cursor: pointer; }

/* Buttons */
.btn { padding: 0.6rem 1.2rem; border-radius: var(--radius); font-size: 0.9rem;
    font-weight: 500; cursor: pointer; border: none; transition: all var(--transition); }
.btn-primary { background: var(--primary); color: var(--white); }
.btn-primary:hover { background: var(--primary-hover); transform: translateY(-1px); }
.btn-outline { background: transparent; color: var(--primary);
    border: 1.5px solid var(--primary); }
.btn-outline:hover { background: var(--primary-light); }
.btn-success { background: var(--success); color: var(--white); }
.btn-danger { background: var(--danger); color: var(--white); }

/* Cards */
.card {
    background: var(--white);
    border-radius: var(--radius);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--gray-200);
}

/* Score Ring */
.score-ring {
    width: 120px; height: 120px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem; font-weight: 700;
    background: conic-gradient(var(--primary) calc(var(--pct) * 3.6deg),
        var(--gray-200) 0deg);
    position: relative;
}
.score-ring::after {
    content: ''; position: absolute; width: 90px; height: 90px;
    background: var(--white); border-radius: 50%;
}
.score-ring span { position: relative; z-index: 1; color: var(--primary); }

/* Kanban Board */
.kanban { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }
.kanban-col { background: var(--gray-100); border-radius: var(--radius); padding: 1rem; }
.kanban-col h3 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;
    color: var(--gray-600); margin-bottom: 0.75rem; }
.kanban-card { background: var(--white); border-radius: 0.5rem; padding: 0.75rem 1rem;
    margin-bottom: 0.5rem; box-shadow: var(--shadow); cursor: grab;
    border-left: 3px solid var(--primary); font-size: 0.85rem; }

/* Responsive */
.main-content { max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem; }
@media (max-width: 768px) {
    .hamburger { display: block; }
    .nav-links { display: none; flex-direction: column; position: absolute;
        top: 60px; left: 0; right: 0; background: var(--white);
        padding: 1rem; border-bottom: 1px solid var(--gray-200); }
    .nav-links.open { display: flex; }
    .kanban { grid-template-columns: 1fr; }
}
```

### `static/js/api.js`

```javascript
/**
 * Central API client — handles auth headers and JSON parsing.
 */
const API_BASE = "/api";

function getToken() {
    return localStorage.getItem("access_token");
}

async function apiFetch(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });

    // Auto-refresh on 401
    if (response.status === 401) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            headers.Authorization = `Bearer ${getToken()}`;
            return fetch(`${API_BASE}${endpoint}`, { ...options, headers });
        } else {
            logout();
            return;
        }
    }

    return response;
}

async function refreshAccessToken() {
    const refresh = localStorage.getItem("refresh_token");
    if (!refresh) return false;
    const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${refresh}`,
            "Content-Type": "application/json",
        },
    });
    if (res.ok) {
        const data = await res.json();
        localStorage.setItem("access_token", data.access_token);
        return true;
    }
    return false;
}

// Helper methods
const API = {
    get: (url) => apiFetch(url),
    post: (url, body) => apiFetch(url, { method: "POST", body: JSON.stringify(body) }),
    delete: (url) => apiFetch(url, { method: "DELETE" }),
    postForm: (url, formData) =>
        apiFetch(url, {
            method: "POST",
            body: formData,
            headers: { Authorization: `Bearer ${getToken()}` },
        }),
};
```

### `static/js/tracker.js`

```javascript
/**
 * Kanban board — drag-and-drop application status tracking
 */
const STATUSES = ["saved", "applied", "interview", "offer", "rejected"];

async function loadTracker() {
    const res = await API.get("/tracker/applications");
    const apps = await res.json();

    STATUSES.forEach((status) => {
        const col = document.getElementById(`col-${status}`);
        if (col) col.innerHTML = "";
    });

    apps.forEach((app) => renderCard(app));
    initDragDrop();
}

function renderCard(app) {
    const col = document.getElementById(`col-${app.status}`);
    if (!col) return;

    const card = document.createElement("div");
    card.className = "kanban-card";
    card.draggable = true;
    card.dataset.id = app._id;
    card.innerHTML = `
        <div class="card-company">${app.job?.company || "Unknown Company"}</div>
        <div class="card-role">${app.job?.title || "Unknown Role"}</div>
        <div class="card-score">ATS: <strong>${app.ats_score}%</strong></div>
        <div class="card-date">${new Date(app.updated_at).toLocaleDateString()}</div>
    `;
    col.appendChild(card);
}

function initDragDrop() {
    const cards = document.querySelectorAll(".kanban-card");
    const cols = document.querySelectorAll(".kanban-col");

    cards.forEach((card) => {
        card.addEventListener("dragstart", (e) => {
            e.dataTransfer.setData("id", card.dataset.id);
        });
    });

    cols.forEach((col) => {
        col.addEventListener("dragover", (e) => e.preventDefault());
        col.addEventListener("drop", async (e) => {
            e.preventDefault();
            const id = e.dataTransfer.getData("id");
            const newStatus = col.dataset.status;
            await API.post(`/tracker/applications/${id}/status`, { status: newStatus });
            await loadTracker();
        });
    });
}

document.addEventListener("DOMContentLoaded", loadTracker);
```

---

## 15. Groq API Integration

Install the official SDK:

```bash
pip install groq
```

The `GroqClient` class in `app/ai/groq_client.py` wraps all Groq calls. All LLM prompts live in `app/ai/prompts.py` for easy iteration.

**Key usage patterns:**

| Task | Groq Prompt | Model |
|---|---|---|
| Resume parsing | `RESUME_PARSE_PROMPT` | llama3-70b-8192 |
| ATS suggestions | `RESUME_SUGGESTIONS_PROMPT` | llama3-70b-8192 |
| Cover letter gen | `COVER_LETTER_PROMPT` | llama3-70b-8192 |
| Skill-gap advice | `SKILL_GAP_ADVICE_PROMPT` | llama3-70b-8192 |

---

## 16. Environment & Configuration

### `.env.example`

```
# Flask
FLASK_ENV=development
SECRET_KEY=your-strong-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# MongoDB
MONGO_URI=mongodb://localhost:27017/career_assistant

# Groq
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Job board API keys
JSEARCH_API_KEY=your-rapidapi-key
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-key
```

---

## 17. Installation & Setup

### Prerequisites

- Python 3.10+
- MongoDB 6.0+ (running locally or MongoDB Atlas)
- Google Chrome + ChromeDriver (auto-managed by `webdriver-manager`)
- Node.js (optional, only if you extend frontend build tooling)

### Step-by-Step

```bash
# 1. Clone and enter project
git clone https://github.com/youruser/career-assistant.git
cd career-assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Copy and configure environment
cp .env.example .env
# Edit .env with your actual keys

# 5. Create uploads directory
mkdir -p uploads/screenshots

# 6. Start MongoDB (if running locally)
mongod --dbpath ./data/db

# 7. (Optional) Seed sample job data
python scripts/seed_jobs.py

# 8. Run the app
python run.py
```

Open `http://localhost:5000` in your browser.

### `requirements.txt`

```
flask==3.0.3
flask-jwt-extended==4.6.0
flask-pymongo==2.3.0
flask-cors==4.0.1
python-dotenv==1.0.1
bcrypt==4.1.3
groq==0.9.0
pdfplumber==0.11.1
python-docx==1.1.2
selenium==4.22.0
webdriver-manager==4.0.1
Werkzeug==3.0.3
pymongo==4.7.3
```

---

## 18. API Endpoints Reference

### Auth (`/api/auth`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register` | — | Register new user |
| POST | `/login` | — | Login, returns JWT tokens |
| POST | `/refresh` | Refresh JWT | Get new access token |
| GET | `/me` | Access JWT | Get current user profile |

### Resume (`/api/resume`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/upload` | ✓ | Upload PDF/DOCX resume |
| GET | `/` | ✓ | List all user resumes |
| DELETE | `/<id>` | ✓ | Delete a resume |

### ATS (`/api/ats`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/score` | ✓ | Score resume vs job description |

### Cover Letter (`/api/cover-letter`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/generate` | ✓ | Generate AI cover letter |
| GET | `/` | ✓ | List user cover letters |

### Jobs (`/api/jobs`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/recommend` | ✓ | Get personalized job matches |
| GET | `/search?q=<query>` | ✓ | Search jobs by keyword |

### Tracker (`/api/tracker`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/applications` | ✓ | Get all user applications |
| POST | `/applications` | ✓ | Save new application |
| PATCH | `/applications/<id>/status` | ✓ | Update application status |
| DELETE | `/applications/<id>` | ✓ | Delete application |

### Auto-Apply (`/api/apply`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/prepare` | ✓ | Preview application before submit |
| POST | `/confirm` | ✓ | Trigger Selenium auto-apply |

---

## 19. Security Considerations

| Concern | Implementation |
|---|---|
| **Password storage** | bcrypt with cost factor 12 |
| **Authentication** | JWT access tokens (1h) + refresh tokens (7d) |
| **File uploads** | `secure_filename()`, extension whitelist, 10 MB limit |
| **Input validation** | Required field checks on all POST endpoints |
| **CORS** | Restricted to `/api/*` prefix |
| **Secrets** | All keys in `.env`, never committed |
| **MongoDB injection** | PyMongo uses typed ObjectId, no raw query string interpolation |
| **Selenium sessions** | Per-request driver, closed after use, never shared |
| **Rate limiting** | Add `flask-limiter` for production (`pip install flask-limiter`) |
| **HTTPS** | Use Nginx + Certbot (Let's Encrypt) in production |

---

## 20. Deployment Guide

### Docker Compose (Recommended)

```yaml
# docker-compose.yml
version: "3.9"
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - MONGO_URI=mongodb://mongo:27017/career_assistant
    env_file: .env
    depends_on:
      - mongo
    volumes:
      - ./uploads:/app/uploads

  mongo:
    image: mongo:7.0
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongo_data:
```

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install Chrome for Selenium
RUN apt-get update && apt-get install -y \
    wget gnupg chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p uploads/screenshots

EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "run:app"]
```

### Build & Run

```bash
docker-compose up --build
```

### Cloud Deployment Options

| Platform | Notes |
|---|---|
| **Render** | Free tier available; add MongoDB Atlas URI |
| **Railway** | One-click Python + MongoDB deployment |
| **AWS EC2** | t3.small sufficient; use MongoDB Atlas for managed DB |
| **Heroku** | Add `heroku-buildpack-chrome-for-testing` for Selenium |

---

## Quick Start Checklist

- [ ] Clone repo and create virtual environment
- [ ] Copy `.env.example` to `.env` and fill in `GROQ_API_KEY` and `MONGO_URI`
- [ ] `pip install -r requirements.txt`
- [ ] Start MongoDB locally or configure MongoDB Atlas URI
- [ ] `python run.py`
- [ ] Register at `http://localhost:5000/api/auth/register`
- [ ] Upload a resume at `POST /api/resume/upload`
- [ ] Run ATS check at `POST /api/ats/score` with a job description
- [ ] Generate cover letter at `POST /api/cover-letter/generate`
- [ ] View job recommendations at `GET /api/jobs/recommend`
- [ ] Use auto-apply at `POST /api/apply/confirm` after user review

---

*Built with Flask · MongoDB · Groq LLM · Selenium · Vanilla JS*
