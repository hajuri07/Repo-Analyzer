# RepoAnalyzer (ReviewForge AI)

An **AI‑powered GitHub repository analysis platform** built with **FastAPI**, **PostgreSQL**, and **Groq LLMs**.  The project now features **asynchronous background processing**, a **status‑polling API**, and a **dark‑mode dashboard** that feels like ChatGPT/Antigravity.

> **Quick start** – after installing dependencies, run:
> ```bash
> uvicorn app.main:app --reload
> ```
> Then open `http://localhost:8000` to see the UI.

---

## 🚀 Key Features

- **✅ JWT authentication** (sign‑up / login)
- **🔁 Asynchronous analysis** – `POST /submission/analyze` returns **202 Accepted** instantly with a tracking ID.
- **📊 Status endpoint** – poll `GET /submission/{id}/status` to see `PENDING`, `PROCESSING`, `COMPLETED`, or `FAILED`.
- **⚡ Server‑Sent Events** – legacy `.../stream` kept for real‑time progress updates.
- **🗂️ Full‑repo cloning** (GitPython) with aggressive black‑listing of non‑code files.
- **🧠 Groq LLM integration** (free model `groq/compound` by default) with **token‑gating** to avoid context over‑flows.
- **🗄️ PostgreSQL persistence** for users, submissions, and structured reviews.
- **🖥️ Dark Antigravity UI** with a live **Job Tracker** panel that shows progress and auto‑redirects to the review view.
- **🧪 Comprehensive test suite** (`pytest`, `httpx.AsyncClient`) covering auth, submission flow, and protected endpoints.

---

## 🛠 Tech Stack

### Backend
- FastAPI
- SQLAlchemy (synchronous sessions, used safely inside BackgroundTasks)
- PostgreSQL
- Pydantic
- JWT (`python‑jose`)

### AI
- Groq API (free `groq/compound` model, fallback to `groq/compound-mini`)

### Git & File Handling
- GitPython
- Aggressive file‑type blacklist + total‑character/token limit

---

## 📐 Architecture

```mermaid
flowchart TD
    User -->|HTTPS| API[FastAPI]
    API -->|JWT auth| Auth[Security]
    Auth -->|valid| Submit[POST /submission/analyze]
    Submit -->|creates row| DB[PostgreSQL]
    Submit -->|BackgroundTasks| Worker[process_submission]
    Worker -->|clone| Git[GitPython]
    Worker -->|read| FileReader[File Reader]
    Worker -->|LLM| Groq[Groq LLM]
    Groq -->|review dict| DB
    DB -->|status updates| API
    API -->|GET /status| Submit
    API -->|GET /review| Review[Review view]
```

- The **worker** runs after the HTTP response has been sent, preventing request‑time‑outs.
- Status updates are persisted in the `submission` table (`status` column) and exposed via `/submission/{id}/status`.

---

## 📁 Project Structure

```
app/
│   main.py            # FastAPI entry point
│   crud.py            # DB helpers & business logic
│   database.py        # Engine & session handling
│   models.py          # SQLAlchemy models (User, Submission, Review)
│   schemas.py         # Pydantic request/response models
│   security.py        # JWT utilities
│
├── Services/
│   ├── ai_review.py          # Groq streaming wrapper
│   ├── github_services.py    # clone / cleanup helpers
│   └── file_reader.py        # token‑gating repo parser
│
├── static/          # Front‑end assets (HTML/CSS/JS)
│   └── index.html
│
└── tests/           # pytest suite (async client, mocks)
    ├── conftest.py
    ├── test_auth.py
    ├── test_submission.py
    └── test_protected.py
```

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/signup` | Register a new user |
| `POST` | `/auth/login`  | Obtain a JWT (`access_token`) |

### Repository Analysis
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/submission/analyze` | Starts analysis, returns **202** with `{submission_id, status:"PENDING"}` |
| `GET`  | `/submission/{id}/status` | Poll current status (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`) and any `error_message` |
| `GET`  | `/submission/{id}` | Retrieve submission metadata (includes status) |
| `GET`  | `/submission/{id}/review` | Get the final structured `ReviewResponse` (only after `COMPLETED`) |
| `GET`  | `/submissions` | List all submissions for the authenticated user |
| `POST` | `/submission/analyze/stream` | Legacy SSE stream (still works) |

---

## 🧪 Testing

```bash
# Install test dependencies (already in requirements.txt)
pytest -q          # run all tests
```

The test suite:
- Creates a temporary user and obtains a JWT.
- Mocks Git cloning, file reading, and Groq calls so no external network traffic occurs.
- Submits a repository, polls the status endpoint until `COMPLETED`, then verifies the stored review.
- Checks that protected routes reject missing or invalid tokens.

---

## 📦 Installation & Quick Start

```bash
# Clone repo
git clone https://github.com/hajuri07/Code-reviewer-.git
cd Code-reviewer-

# Create a virtual environment (optional but recommended)
python -m venv .venv && .\.venv\Scripts\activate   # Windows PowerShell
# or: source .venv/bin/activate   # Unix

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env   # edit the values
# .env should contain at least:
# DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/codereview
# SECRET_KEY= <a‑long‑random‑string>
# GROQ_API_KEY=your_groq_key

# Run the API
uvicorn app.main:app --reload
```

Open `http://localhost:8000` in a browser, sign‑up, and start analyzing repositories!

---

## 🚧 Future Improvements
- **Celery / Redis queue** for truly distributed background workers.
- **Docker Compose** for one‑click dev/prod environments.
- **Multi‑LLM support** (e.g., Gemini, Claude) with automatic model selection.
- **PDF report generation** and email delivery of review results.
- **Dashboard** showing review history, metrics, and trends.
- **Pull‑request review mode** – analyze PR diffs instead of whole repos.

---

## ✍️ Author

**Ibrahim Hajuri** –AI Engineer

Feel free to open issues or PRs – the project is designed to be a learning playground for AI‑assisted code analysis.
