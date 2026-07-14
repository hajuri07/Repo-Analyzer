# 🤖 RepoAnalyzer

An AI-powered GitHub Repository Analysis API built with **FastAPI**, **PostgreSQL**, and **Groq LLMs**.

Instead of reviewing a single pasted code snippet, RepoAnalyzer AI clones an entire GitHub repository, extracts relevant source files, analyzes the project architecture using an LLM, and stores structured reviews for authenticated users.

---

## 🚀 Features

- 🔐 JWT Authentication
- 👤 User Registration & Login
- 📦 GitHub Repository Cloning
- 📂 Automatic Repository Parsing
- 🤖 AI-powered Repository Analysis
- 📝 Repository Review History
- 🗄️ PostgreSQL Database
- ⚡ FastAPI REST API
- 🔑 Protected Endpoints

---

## 🛠 Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT Authentication

### AI

- Groq API
- Llama 3.3 70B

### Git

- GitPython

---

## 🏗 Architecture

```text
User
 │
 ▼
FastAPI API
 │
 ▼
JWT Authentication
 │
 ▼
Submission Endpoint
 │
 ▼
Clone GitHub Repository
 │
 ▼
Read Repository Files
 │
 ▼
Groq LLM
 │
 ▼
JSON Review
 │
 ▼
PostgreSQL
```

---

## 📁 Project Structure

```text
app/
│
├── crud.py
├── database.py
├── main.py
├── models.py
├── schemas.py
├── security.py
│
├── services/
│   ├── ai_service.py
│   ├── github_service.py
│   └── file_reader.py
│
└── temp/
```

---

## 🔍 AI Review Includes

The LLM evaluates repositories based on:

- Architecture
- Code Quality
- Maintainability
- Readability
- Performance
- Security
- Best Practices
- Folder Structure
- Design Patterns
- Error Handling
- Documentation

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description |
|----------|----------------------|----------------|
| POST | `/auth/signup` | Register User |
| POST | `/auth/login` | Login |

---

### Repository Analysis

| Method | Endpoint | Description |
|----------|----------------------------|----------------|
| POST | `/submission/analyze` | Analyze GitHub Repository |
| GET | `/submission/{id}` | Get Submission |
| GET | `/submission/{id}/review` | Get AI Review |

---

## Example Request

```json
POST /submission/analyze

{
    "repo_url": "https://github.com/tiangolo/fastapi"
}
```

---

## Example Response

```json
{
    "overall_score": 8.7,
    "summary": "Well-structured FastAPI project following modern best practices.",
    "issues": [
        "Missing unit tests for authentication module.",
        "Large router could be further modularized."
    ],
    "suggestions": [
        "Increase test coverage.",
        "Improve API documentation."
    ]
}
```

---

## Installation

```bash
git clone https://github.com/yourusername/repository-analyzer.git

cd repository-analyzer

pip install -r requirements.txt
```

Create a `.env`

```env
DATABASE_URL=...

SECRET_KEY=...

GROQ_API_KEY=...
```

Run

```bash
uvicorn app.main:app --reload
```

---

## Future Improvements

- Repository History Dashboard
- Background Task Queue (Celery)
- Async Repository Analysis
- Docker Support
- Multi-LLM Support
- Repository Metrics
- Pull Request Review
- PDF Report Generation
- Deployment Support

---

## Author

**Ibrahim Hajuri**

Backend Developer | Applied AI Engineer
