"""
scripts/seed_jobs.py
Seed the MongoDB `jobs` collection with sample job data for development/testing.
Usage: python scripts/seed_jobs.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
import random
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/career_assistant")

SAMPLE_JOBS = [
    {
        "title": "Senior Data Scientist",
        "company": "Google",
        "location": "Mountain View, CA / Remote",
        "description": "Join our data science team to build state-of-the-art ML models. You'll work on large-scale data pipelines, develop predictive algorithms, and drive data-informed product decisions across Google's core products.",
        "required_skills": ["Python", "TensorFlow", "BigQuery", "SQL", "Machine Learning", "Deep Learning"],
        "experience_level": "Senior",
        "job_type": "Full-time",
        "apply_url": "https://careers.google.com/jobs/data-scientist",
        "source": "LinkedIn",
        "posted_at": datetime.utcnow() - timedelta(days=2),
        "scraped_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "title": "Full Stack Engineer",
        "company": "Stripe",
        "location": "San Francisco, CA / Remote",
        "description": "Build and scale Stripe's payments infrastructure. Work with React, Node.js, and distributed systems to create reliable, high-performance financial services used by millions of businesses worldwide.",
        "required_skills": ["JavaScript", "TypeScript", "React", "Node.js", "PostgreSQL", "REST API"],
        "experience_level": "Mid",
        "job_type": "Full-time",
        "apply_url": "https://stripe.com/jobs/full-stack-engineer",
        "source": "Indeed",
        "posted_at": datetime.utcnow() - timedelta(days=1),
        "scraped_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "title": "Machine Learning Engineer",
        "company": "OpenAI",
        "location": "San Francisco, CA",
        "description": "Research and develop cutting-edge AI systems. Work on large language models, reinforcement learning from human feedback, and safety research to build powerful and safe AI systems.",
        "required_skills": ["Python", "PyTorch", "Machine Learning", "Deep Learning", "NLP", "CUDA"],
        "experience_level": "Senior",
        "job_type": "Full-time",
        "apply_url": "https://openai.com/careers/ml-engineer",
        "source": "LinkedIn",
        "posted_at": datetime.utcnow() - timedelta(days=3),
        "scraped_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "title": "Backend Engineer – Python",
        "company": "Airbnb",
        "location": "Remote",
        "description": "Design and build robust backend services for Airbnb's marketplace. You'll architect scalable APIs, optimize database performance, and collaborate with cross-functional teams to deliver high-impact features.",
        "required_skills": ["Python", "Django", "PostgreSQL", "Redis", "AWS", "Docker"],
        "experience_level": "Mid",
        "job_type": "Full-time",
        "apply_url": "https://careers.airbnb.com/backend-engineer",
        "source": "Greenhouse",
        "posted_at": datetime.utcnow() - timedelta(days=5),
        "scraped_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "title": "Data Engineer",
        "company": "Spotify",
        "location": "Stockholm / Remote",
        "description": "Build and maintain Spotify's data infrastructure. Create scalable data pipelines using Apache Spark and Airflow, design data models, and support analytics teams across the business.",
        "required_skills": ["Python", "Spark", "Airflow", "SQL", "GCP", "Kafka"],
        "experience_level": "Mid",
        "job_type": "Full-time",
        "apply_url": "https://www.lifeatspotify.com/jobs/data-engineer",
        "source": "LinkedIn",
        "posted_at": datetime.utcnow() - timedelta(days=4),
        "scraped_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "title": "DevOps / Cloud Engineer",
        "company": "Netflix",
        "location": "Los Gatos, CA / Remote",
        "description": "Manage and improve Netflix's cloud infrastructure at massive scale. Work with Kubernetes, Terraform, and AWS to ensure high availability and reliability for hundreds of millions of streaming users.",
        "required_skills": ["Kubernetes", "Docker", "AWS", "Terraform", "CI/CD", "Linux"],
        "experience_level": "Senior",
        "job_type": "Full-time",
        "apply_url": "https://jobs.netflix.com/devops-engineer",
        "source": "LinkedIn",
        "posted_at": datetime.utcnow() - timedelta(days=6),
        "scraped_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "title": "Frontend Engineer – React",
        "company": "Figma",
        "location": "San Francisco, CA / Remote",
        "description": "Shape the future of design tools at Figma. Build interactive, pixel-perfect UIs using React and TypeScript. Work closely with designers to create extraordinary user experiences.",
        "required_skills": ["JavaScript", "TypeScript", "React", "CSS", "WebGL", "Next.js"],
        "experience_level": "Mid",
        "job_type": "Full-time",
        "apply_url": "https://www.figma.com/careers/frontend-engineer",
        "source": "Greenhouse",
        "posted_at": datetime.utcnow() - timedelta(days=2),
        "scraped_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "title": "Software Engineer – Go",
        "company": "HashiCorp",
        "location": "Remote",
        "description": "Build open-source infrastructure tools used by thousands of companies. Work on Terraform, Vault, and Consul using Go. Collaborate with a distributed team to create reliable cloud tooling.",
        "required_skills": ["Go", "Terraform", "AWS", "Docker", "Kubernetes", "Linux"],
        "experience_level": "Mid",
        "job_type": "Full-time",
        "apply_url": "https://www.hashicorp.com/jobs/software-engineer-go",
        "source": "LinkedIn",
        "posted_at": datetime.utcnow() - timedelta(days=7),
        "scraped_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "title": "Data Analyst",
        "company": "Shopify",
        "location": "Remote",
        "description": "Analyze merchant and buyer behavior to drive product insights. Build dashboards with Tableau and Power BI, write complex SQL queries, and communicate findings to cross-functional stakeholders.",
        "required_skills": ["SQL", "Python", "Tableau", "Power BI", "dbt", "PostgreSQL"],
        "experience_level": "Junior",
        "job_type": "Full-time",
        "apply_url": "https://www.shopify.com/careers/data-analyst",
        "source": "Indeed",
        "posted_at": datetime.utcnow() - timedelta(days=1),
        "scraped_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "title": "Platform Engineer",
        "company": "Datadog",
        "location": "New York, NY / Remote",
        "description": "Build internal developer platforms and tooling to improve engineering productivity at Datadog. Work on CI/CD infrastructure, build systems, and developer experience tooling at scale.",
        "required_skills": ["Python", "Go", "Kubernetes", "Docker", "GitHub Actions", "Jenkins"],
        "experience_level": "Senior",
        "job_type": "Full-time",
        "apply_url": "https://www.datadoghq.com/careers/platform-engineer",
        "source": "LinkedIn",
        "posted_at": datetime.utcnow() - timedelta(days=3),
        "scraped_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "title": "AI/ML Research Scientist",
        "company": "Meta AI",
        "location": "Menlo Park, CA / Remote",
        "description": "Conduct original research in ML, computer vision, and natural language processing. Publish in top venues (NeurIPS, ICML, ICLR) and translate research into production AI systems at Meta's scale.",
        "required_skills": ["Python", "PyTorch", "Machine Learning", "Deep Learning", "NLP", "Computer Vision"],
        "experience_level": "Senior",
        "job_type": "Full-time",
        "apply_url": "https://about.meta.com/careers/ml-research-scientist",
        "source": "LinkedIn",
        "posted_at": datetime.utcnow() - timedelta(days=2),
        "scraped_at": datetime.utcnow(),
        "is_active": True,
    },
    {
        "title": "Product Manager – AI Tools",
        "company": "Notion",
        "location": "San Francisco, CA",
        "description": "Lead the product vision for Notion AI. Work with engineers and designers to ship AI-powered features that help millions of users write, organize, and think better.",
        "required_skills": ["Product Management", "SQL", "Python", "Machine Learning", "Agile", "Data Analysis"],
        "experience_level": "Mid",
        "job_type": "Full-time",
        "apply_url": "https://www.notion.so/careers/product-manager-ai",
        "source": "LinkedIn",
        "posted_at": datetime.utcnow() - timedelta(days=4),
        "scraped_at": datetime.utcnow(),
        "is_active": True,
    },
]


def seed():
    client = MongoClient(MONGO_URI)
    db_name = MONGO_URI.split("/")[-1]
    db = client[db_name]

    collection = db["jobs"]
    
    # Clear existing seed data
    deleted = collection.delete_many({"source": {"$in": ["LinkedIn", "Indeed", "Greenhouse"]}})
    print(f"Cleared {deleted.deleted_count} existing seed jobs.")

    result = collection.insert_many(SAMPLE_JOBS)
    print(f"Seeded {len(result.inserted_ids)} sample jobs into '{db_name}.jobs'")
    
    client.close()


if __name__ == "__main__":
    seed()
