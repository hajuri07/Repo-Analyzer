import json
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas, security
from .database import Base, engine, ensure_review_columns, get_db

app = FastAPI(title="ReviewForge AI", version="1.0.0", description="Secure, streamed GitHub repository reviews.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)
ensure_review_columns()


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "service": "ReviewForge AI"}


@app.post("/auth/signup", response_model=schemas.UserResponse, status_code=201)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(user, db)


@app.post("/auth/login", response_model=schemas.Token)
def user_login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    return crud.user_login(user, db)


@app.get("/auth/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only access your own profile")
    return crud.read_user(user_id, db)


@app.post("/submission/analyze", response_model=schemas.SubmissionResponse, status_code=202)
def analyze(submission: schemas.SubmissionCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    # Create submission record with default status PENDING
    record = models.Submission(user_id=current_user.id, repo_url=str(submission.repo_url))
    db.add(record)
    db.commit()
    db.refresh(record)
    # Schedule background processing
    from app.services.worker import process_submission
    background_tasks.add_task(process_submission, record.id)
    return record

# Removed legacy synchronous analyze endpoint – now handled via background tasks
# def analyze(submission: schemas.SubmissionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
#     return crud.create_submission(submission, db, current_user)



@app.post("/submission/analyze/stream")
def analyze_stream(submission: schemas.SubmissionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    def events():
        for event in crud.analyze_submission(submission, db, current_user):
            yield f"event: {event['stage']}\ndata: {json.dumps(event)}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/submissions", response_model=list[schemas.SubmissionResponse])
def list_user_submissions(db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    return crud.get_user_submissions(db, current_user)


@app.get("/submission/{submission_id}/status", response_model=schemas.SubmissionResponse)
def get_submission_status(submission_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    sub = crud.get_submission(db, submission_id, current_user)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found or not yours")
    return sub

def get_submission(submission_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    result = crud.get_submission(db, submission_id, current_user)
    if not result:
        raise HTTPException(status_code=404, detail="Submission not found or not yours")
    return result


@app.get("/submission/{submission_id}/review", response_model=schemas.ReviewResponse)
def get_review(submission_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    return crud.get_review(submission_id, current_user, db)

