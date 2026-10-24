from collections.abc import Generator

from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas, security
from app.Services.ai_review import stream_repository_review
from app.Services.file_reader import read_repo
from app.Services.github_services import clone_repository, remove_cloned_repository


def create_user(user: schemas.UserCreate, db: Session):
    existing = db.query(models.User).filter((models.User.username == user.username) | (models.User.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username or email already exists.")
    new_user = models.User(username=user.username, email=user.email, hashed_password=security.hash_password(user.password))
    db.add(new_user); db.commit(); db.refresh(new_user)
    return new_user


def read_user(user_id: int, db: Session):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def user_login(credentials: schemas.UserLogin, db: Session):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not security.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})
    return schemas.Token(access_token=security.create_access_token(user.id), token_type="bearer")


def analyze_submission(submission: schemas.SubmissionCreate, db: Session, current_user: models.User) -> Generator[dict, None, None]:
    record = models.Submission(user_id=current_user.id, repo_url=str(submission.repo_url))
    db.add(record); db.commit(); db.refresh(record)
    yield {"stage": "accepted", "message": "Repository queued securely.", "submission_id": record.id}
    repo_path = None
    try:
        yield {"stage": "cloning", "message": "Cloning the latest public commit…"}
        repo_path = clone_repository(str(submission.repo_url))
        yield {"stage": "indexing", "message": "Reading supported source files…"}
        source = read_repo(repo_path)
        if not source:
            raise ValueError("No supported source files were found in this repository.")
        yield {"stage": "reviewing", "message": "AI is evaluating architecture, quality, and security…"}
        result = None
        for event in stream_repository_review(source):
            if event["type"] == "chunk":
                yield {"stage": "generating", "message": "AI is generating the review…", "delta": event["text"]}
            elif event["type"] == "heartbeat":
                yield {"stage": "generating", "message": "AI is evaluating code quality, security, and architecture…"}
            else:
                result = event["review"]
        if result is None:
            raise RuntimeError("The AI provider returned no review.")
        review = models.Review(submission_id=record.id, summary=result["summary"], issues=result["issues"], suggestions=result["suggestions"], overall_score=result["overall_score"], metrics=result["metrics"], roadmap=result["roadmap"])
        db.add(review); db.commit(); db.refresh(review)
        yield {"stage": "complete", "message": "Review is ready.", "submission_id": record.id, "review": result}
    except (ValueError, RuntimeError) as exc:
        db.rollback()
        yield {"stage": "error", "message": str(exc)}
    finally:
        if repo_path:
            remove_cloned_repository(repo_path)


def create_submission(submission: schemas.SubmissionCreate, db: Session, current_user: models.User):
    result = None
    for result in analyze_submission(submission, db, current_user):
        pass
    if not result or result["stage"] == "error":
        raise HTTPException(status_code=422, detail=(result or {}).get("message", "Analysis failed"))
    return get_submission(db, result["submission_id"], current_user)


def get_submission(db: Session, submission_id: int, current_user: models.User):
    return db.query(models.Submission).filter(models.Submission.id == submission_id, models.Submission.user_id == current_user.id).first()


def get_user_submissions(db: Session, current_user: models.User):
    return db.query(models.Submission).filter(models.Submission.user_id == current_user.id).order_by(models.Submission.submitted_at.desc()).all()


def get_review(submission_id: int, current_user: models.User, db: Session):
    submission = get_submission(db, submission_id, current_user)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found or not yours")
    if not submission.review:
        raise HTTPException(status_code=404, detail="Review not found")
    return submission.review

