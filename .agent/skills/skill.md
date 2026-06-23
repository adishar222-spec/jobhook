# Antigravity Skill — Resume Auto-Apply System

**Tech Stack:** HTML · CSS · JavaScript · Flask · Python · MongoDB · Groq API · Selenium

---

## Overview

Antigravity is a **complete resume automation platform** that helps job seekers upload or build resumes, get AI-powered optimization suggestions, search for matching jobs, and automatically apply to positions using Selenium web automation.

The project spans full-stack development: frontend (HTML/CSS/JS), backend (Flask/Python), database (MongoDB), AI integration (Groq API), and browser automation (Selenium).

---

## When to Use This Skill

Trigger this skill when:

- Building or maintaining the Antigravity resume auto-apply system
- Implementing new features for the Groq API integration (replacing OpenAI)
- Working with MongoDB collections for user data, resumes, or applications
- Writing Selenium automation for new job board handlers
- Creating or modifying Flask routes for auth, resume management, jobs, or AI suggestions
- Designing frontend forms (resume builder, job search, AI suggestions UI)
- Debugging issues related to PDF generation, job scraping, or auto-apply workflows
- Setting up MongoDB indexes for performance optimization
- Implementing resume parsing (PDF/DOCX extraction)
- Handling resume-to-job-description comparisons and gap analysis

Do NOT use this skill for:
- Unrelated projects (use appropriate skill for that project instead)
- General Python/Flask questions (use those foundational skills)
- Generic MongoDB questions (unless Antigravity-specific)

---

## Project Architecture

### 5-Layer System

```
Layer 1: Authentication
├── Register: username, email, password
├── Bcrypt hashing
└── Flask-Login session management

Layer 2: Resume Management
├── Upload path: PDF/DOCX → PyPDF2/python-docx → MongoDB
└── Builder path: Form → ReportLab PDF → MongoDB

Layer 3: AI Optimization
├── User inputs job description
├── Groq API compares resume vs JD
├── Returns gap analysis + suggestions
└── Course recommendation matcher

Layer 4: Job Search & Auto-Apply
├── BeautifulSoup scrapes Indeed
├── Selenium applies (LinkedIn/Indeed/Naukri)
└── MongoDB logs applications

Layer 5: Database
├── users collection
├── resumes collection
└── applications collection
```

---

## Tech Stack Details

### Frontend (HTML · CSS · JavaScript)

**HTML Templates:**
- `base.html` — navigation, flash messages, base layout
- `auth/login.html`, `auth/register.html` — authentication forms
- `resume/upload.html` — resume upload + builder option
- `resume/builder.html` — multi-step form (personal info, experience, education, skills)
- `suggestions.html` — AI suggestions + course recommendations
- `jobs.html` — job search form + application history table

**CSS Styling:**
- `style.css` — responsive grid layouts, cards, buttons, forms, alerts, badges
- Colors: dark theme with navy (#1a1a2e), teal accents
- Utilities: .btn-primary, .btn-outline, .card, .badge, .alert-*, .form-group

**JavaScript Interactions:**
- Dynamic form entry adders (addExperience, addEducation)
- File upload drag-and-drop feedback
- Form submission loading states
- Confirmation dialogs before Selenium auto-apply

### Backend (Flask · Python)

**Flask Structure:**
```
app/__init__.py (app factory)
├── config.py (CONFIG class, environment variables)
├── db.py (MongoDB connection, MongoUser wrapper)
├── routes/
│   ├── auth.py (/auth/register, /auth/login, /auth/logout)
│   ├── resume.py (/resume, /resume/upload, /resume/builder)
│   ├── ai_suggestions.py (/ai/suggestions, /ai/suggestions/api)
│   └── jobs.py (/jobs, /jobs/search, /jobs/apply)
├── services/
│   ├── resume_parser.py (PyPDF2 + python-docx)
│   ├── pdf_generator.py (ReportLab)
│   ├── ai_service.py (Groq API integration)
│   ├── job_scraper.py (BeautifulSoup + requests)
│   └── selenium_apply.py (Selenium automation)
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/ (all HTML files)
```

**Key dependencies:**
- `flask` — web framework
- `flask-login` — session management
- `flask-bcrypt` — password hashing
- `pymongo` — MongoDB driver
- `groq` — Groq API client (replaces OpenAI)
- `selenium` — browser automation
- `beautifulsoup4` — HTML parsing
- `requests` — HTTP client
- `reportlab` — PDF generation
- `PyPDF2` — PDF text extraction
- `python-docx` — DOCX parsing

### Database (MongoDB)

**Three Collections:**

#### 1. `users`
```json
{
  "_id": ObjectId,
  "username": "janedoe",
  "email": "jane@example.com",
  "password": "$2b$12$hashed...",
  "created_at": ISODate
}
```
Indexes: unique on `email`, `username`

#### 2. `resumes`
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "filename": "resume_userid_resumeid.pdf",
  "content": "extracted plain text...",
  "is_active": true,
  "created_at": ISODate,
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+91 9876543210",
  "location": "Kozhikode, Kerala",
  "summary": "Full-stack developer...",
  "experience": [
    {
      "company": "Acme Corp",
      "role": "Software Engineer",
      "date": "Jan 2023 – Present",
      "description": "Built REST APIs..."
    }
  ],
  "education": [
    {
      "school": "University of Calicut",
      "degree": "B.Tech CS",
      "year": "2019 – 2023"
    }
  ],
  "skills": ["Python", "Flask", "React", "MongoDB"]
}
```
Indexes: compound `[user_id, is_active]`

#### 3. `applications`
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "resume_id": ObjectId,
  "job_title": "Backend Developer",
  "company": "TCS",
  "job_url": "https://...",
  "status": "applied|failed|pending",
  "applied_at": ISODate,
  "notes": "Applied via Indeed"
}
```
Indexes: compound `[user_id, job_url]` (prevents duplicates)

### AI Integration (Groq API)

**File:** `app/services/ai_service.py`

**Purpose:** Compare resume against job description, identify gaps, suggest improvements.

**Usage:**
```python
from app.services.ai_service import get_resume_suggestions, suggest_courses

# Get AI suggestions
suggestions_html = get_resume_suggestions(resume_text, job_description)

# Get course recommendations
courses = suggest_courses(job_description)
```

**Key function:**
```python
def get_resume_suggestions(resume_text, job_description):
    """
    Sends resume + JD to Groq API.
    Prompt asks for:
    1. Missing keywords (5-8)
    2. Skills to add
    3. Experience improvements
    4. Tailored summary rewrite
    5. Overall match score (out of 10)
    
    Returns HTML-formatted suggestions.
    """
    prompt = f"""
    You are an expert resume coach. Compare the resume below 
    with the job description and provide structured feedback...
    
    RESUME:
    {resume_text[:3000]}
    
    JOB DESCRIPTION:
    {job_description[:2000]}
    """
    
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",  # Groq model
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7
    )
    
    return _markdown_to_html(response.choices[0].message.content)
```

**Course database:**
```python
COURSE_DB = [
    {
        'name': 'Machine Learning Specialization',
        'provider': 'Coursera / Stanford',
        'keywords': ['machine learning', 'ml', 'tensorflow', 'neural'],
        'url': '...'
    },
    # ... 7 more courses (AWS, Data Analytics, Frontend, etc.)
]
```

Keyword matching returns up to 5 relevant courses based on JD content.

### Browser Automation (Selenium)

**File:** `app/services/selenium_apply.py`

**Purpose:** Automatically fill job application forms and submit.

**Supported platforms:**
- LinkedIn Easy Apply
- Indeed
- Naukri
- Generic fallback (common form selectors)

**Core function:**
```python
def apply_to_job(job_url, resume_doc):
    """
    Dispatcher routes to correct handler based on domain.
    Returns (success: bool, message: str)
    """
    if 'linkedin.com' in job_url:
        return _apply_linkedin(job_url, resume_doc)
    elif 'indeed.com' in job_url:
        return _apply_indeed(job_url, resume_doc)
    elif 'naukri.com' in job_url:
        return _apply_naukri(job_url, resume_doc)
    else:
        return _apply_generic(job_url, resume_doc)
```

**Selenium workflow for Indeed:**
```
1. Get Chrome driver (headless=True, anti-detection options)
2. driver.get(job_url)
3. Wait for Apply button to load
4. Click Apply button
5. Fill form fields:
   - input[name="name"] → resume.full_name
   - input[name="email"] → resume.email
   - input[name="phone"] → resume.phone
6. Upload PDF: input[type="file"].send_keys(pdf_path)
7. Click Submit button
8. Wait for confirmation
9. driver.quit()
10. Return (True, "Applied via Indeed")
```

**Important notes:**
- Use `headless=False` for LinkedIn (bot detection)
- Add human-like delays: `time.sleep(random.uniform(0.5, 2))`
- Resume PDF must exist at: `/resumes/resume_userid_resumeid.pdf`
- User must confirm via JavaScript dialog before applying
- Each application logged to MongoDB with status + notes

---

## Key Workflows

### 1. User Registration & Login
```
Register → Bcrypt hash password → Insert to db.users → Login → Flask-Login session
```

### 2. Resume Management
```
Upload PDF/DOCX → PyPDF2/python-docx extract text → ReportLab PDF gen → db.resumes insert

OR

Fill builder form → Collect experience/education/skills as arrays → ReportLab PDF gen → db.resumes insert
```

### 3. AI Gap Analysis
```
User pastes JD → Groq API prompt (resume vs JD) → GPT response (markdown) → Convert to HTML → Display

Simultaneously: Keyword matcher → COURSE_DB lookup → Return matching courses
```

### 4. Job Search
```
User enters keywords + location → requests.get(indeed.com/jobs?q=...) → BeautifulSoup parse → Extract 20 jobs → Display

User clicks "Auto-apply" → Confirm dialog → Selenium dispatcher → Handler fills form → Submit → db.applications update
```

### 5. Application History
```
db.applications.find({user_id: ObjectId(user_id)}) → Sort by applied_at desc → Display in table
```

---

## Common Implementation Patterns

### MongoDB Operations

**Insert document:**
```python
from app.db import get_db
from bson import ObjectId
from datetime import datetime

db = get_db()
db.resumes.insert_one({
    'user_id': ObjectId(user_id),
    'filename': 'resume.pdf',
    'content': 'extracted text...',
    'is_active': True,
    'created_at': datetime.utcnow(),
    'experience': [],
    'skills': ['Python', 'Flask']
})
```

**Find with index:**
```python
# Uses compound index [user_id, is_active]
resume = db.resumes.find_one({
    'user_id': ObjectId(user_id),
    'is_active': True
})
```

**Update document:**
```python
db.applications.update_one(
    {'_id': ObjectId(app_id)},
    {'$set': {'status': 'applied', 'notes': message}}
)
```

**Deactivate old resumes:**
```python
db.resumes.update_many(
    {'user_id': ObjectId(user_id)},
    {'$set': {'is_active': False}}
)
```

### Flask Routes

**Protected route (requires login):**
```python
from flask_login import login_required, current_user

@app.route('/resume')
@login_required
def resume():
    user_id = current_user.id  # ObjectId as string
    resume = get_db().resumes.find_one({
        'user_id': ObjectId(user_id),
        'is_active': True
    })
    return render_template('resume/upload.html', resume=resume)
```

**Form handling with arrays:**
```python
@app.route('/resume/builder', methods=['POST'])
@login_required
def builder():
    data = request.form
    
    # Collect array fields
    experience = []
    for i, company in enumerate(data.getlist('exp_company[]')):
        experience.append({
            'company': company,
            'role': data.getlist('exp_role[]')[i],
            'date': data.getlist('exp_date[]')[i],
            'description': data.getlist('exp_desc[]')[i]
        })
    
    skills = [s.strip() for s in data.get('skills', '').split(',') if s.strip()]
    
    # Save to MongoDB
    db = get_db()
    db.resumes.insert_one({
        'user_id': ObjectId(current_user.id),
        'experience': experience,
        'skills': skills,
        # ... other fields
    })
```

### Groq API Integration

```python
from groq import Groq

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def get_resume_suggestions(resume_text, job_description):
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{
            "role": "user",
            "content": f"Compare resume vs JD:\n\nRESUME:\n{resume_text}\n\nJD:\n{job_description}"
        }],
        max_tokens=1000,
        temperature=0.7
    )
    return response.choices[0].message.content
```

### Selenium Form Filling

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def _apply_indeed(job_url, resume_doc):
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(job_url)
        wait = WebDriverWait(driver, 10)
        
        # Wait for button
        apply_btn = wait.until(
            EC.element_to_be_clickable((By.ID, 'indeedApplyButton'))
        )
        apply_btn.click()
        time.sleep(2)
        
        # Fill fields
        driver.find_element(By.CSS_SELECTOR, 'input[name="name"]').send_keys(
            resume_doc.get('full_name', '')
        )
        driver.find_element(By.CSS_SELECTOR, 'input[name="email"]').send_keys(
            resume_doc.get('email', '')
        )
        
        # Upload resume
        file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        file_input.send_keys(os.path.join(os.getcwd(), 'resumes', resume_doc['filename']))
        
        # Submit
        submit = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit.click()
        
        return True, "Applied via Indeed"
    except Exception as e:
        return False, str(e)
    finally:
        driver.quit()
```

---

## Setup & Configuration

### Environment Variables (.env)

```
SECRET_KEY=your-secret-flask-key
MONGO_URI=mongodb://localhost:27017/resume_db
# OR for MongoDB Atlas:
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/resume_db?retryWrites=true&w=majority

GROQ_API_KEY=gsk_your_groq_api_key_here
```

### MongoDB Indexes (Run Once)

```python
from app import create_app
from app.db import get_db
from bson import ObjectId

app = create_app()
with app.app_context():
    db = get_db()
    
    # Users
    db.users.create_index("email", unique=True)
    db.users.create_index("username", unique=True)
    
    # Resumes
    db.resumes.create_index([("user_id", 1), ("is_active", 1)])
    
    # Applications
    db.applications.create_index([("user_id", 1), ("job_url", 1)])
    
    print("Indexes created successfully")
```

### Installation

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Start MongoDB
mongod --dbpath /data/db

# Run Flask
python run.py
```

---

## Best Practices

### 1. Always Use Indexes
- Compound indexes on frequently queried field combinations
- Example: `[user_id, is_active]` for resume lookups
- Example: `[user_id, job_url]` for duplicate prevention

### 2. Deactivate Before Inserting
Always mark old resumes as inactive before inserting new ones:
```python
db.resumes.update_many({'user_id': ObjectId(user_id)}, {'$set': {'is_active': False}})
db.resumes.insert_one({...new resume...})
```

### 3. Convert ObjectId to String in Templates
```python
# In Flask
return render_template('template.html', user_id=str(current_user.id))

# In template
<input type="hidden" value="{{ user_id }}"/>
```

### 4. Store Arrays as Native MongoDB Lists
Don't use JSON strings. MongoDB handles lists natively:
```python
# GOOD
resume_doc = {'skills': ['Python', 'Flask', 'MongoDB']}

# BAD
resume_doc = {'skills': '["Python", "Flask", "MongoDB"]'}
```

### 5. Use Confirmation Dialogs Before Selenium
Always ask user to confirm before auto-applying:
```javascript
if (!confirm('Apply to ' + jobTitle + ' at ' + company + '?')) {
    return false;
}
```

### 6. Add Human-Like Delays in Selenium
```python
import random, time

def human_delay(min_sec=0.5, max_sec=2.0):
    time.sleep(random.uniform(min_sec, max_sec))
```

### 7. Error Handling in Selenium
Always use try-finally to quit the driver:
```python
driver = get_driver()
try:
    # ... automation logic ...
except Exception as e:
    return False, str(e)
finally:
    driver.quit()
```

---

## Common Gotchas & Solutions

| Issue | Solution |
|---|---|
| Selenium times out on LinkedIn | Use `headless=False` and login via browser first |
| PDF upload fails | Ensure file exists at correct path: `/resumes/filename.pdf` |
| Groq API returns incomplete response | Increase `max_tokens` or use streaming if available |
| MongoDB index not working | Create index with exact field order used in query |
| Bcrypt hash verification fails | Ensure password is decoded to string: `bcrypt.check_password_hash(hash_string, plain_text)` |
| Resume text extraction is garbled | Use `PyPDF2` for PDFs, `python-docx` for DOCX, may need manual cleanup |
| Duplicate applications stored | Check compound index on `[user_id, job_url]` is created |
| CAPTCHA blocking auto-apply | Use 2Captcha/CapSolver service or retry with human verification |

---

## Future Enhancements

1. **Dashboard** — Kanban board of applications (applied, viewed, rejected, interview)
2. **Cover letter generator** — AI generates tailored cover letters
3. **Application analytics** — Track response rates by job title, company, skills
4. **Browser extension** — Run directly in user's browser (avoids bot detection)
5. **Email notifications** — Alert user when they receive responses
6. **Resume versioning** — Store multiple resumes, choose which to apply with
7. **Job board APIs** — Use Adzuna, Reed, Remotive APIs instead of scraping
8. **Celery + Redis** — Background jobs for Selenium (avoid blocking HTTP requests)
9. **Multi-language support** — Resume optimization in different languages
10. **Salary negotiation tips** — AI advises on salary ranges based on job description

---

## Testing

### Manual testing checklist:
- [ ] Register new user
- [ ] Login with correct + incorrect credentials
- [ ] Upload PDF resume (ensure text extracts correctly)
- [ ] Build resume from form (verify PDF generates)
- [ ] Paste job description (verify Groq API returns suggestions)
- [ ] Search jobs (verify Indeed scraping returns results)
- [ ] Click auto-apply (confirm dialog appears)
- [ ] Check application logged to MongoDB
- [ ] View application history table
- [ ] Logout and relogin (session persists)

### Example Groq API test:
```python
from app.services.ai_service import get_resume_suggestions

resume = "Jane Doe, Backend Developer, 5 years Python, Flask experience..."
jd = "Senior Backend Developer needed. Required: 3+ years Python, Docker, AWS..."

suggestions = get_resume_suggestions(resume, jd)
print(suggestions)
# Output: HTML-formatted suggestions
```

---

## References

- **MongoDB documentation:** https://docs.mongodb.com/
- **Groq API docs:** https://console.groq.com/docs
- **Selenium docs:** https://selenium.dev/documentation/
- **Flask docs:** https://flask.palletsprojects.com/
- **BeautifulSoup:** https://www.crummy.com/software/BeautifulSoup/
- **ReportLab:** https://www.reportlab.com/docs/reportlab-userguide.pdf