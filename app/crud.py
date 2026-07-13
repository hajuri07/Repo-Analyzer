from fastapi import  HTTPException, status
from . import schemas
from . import models
from .import security
from sqlalchemy.orm import Session
from app.database import get_db
from app import service

def create_user(user: schemas.UserCreate ,db: Session):
    db_user = db.query(models.User).filter((models.User.username == user.username) | (models.User.email == user.email)).first()
 
    if db_user:
            raise HTTPException(status_code =status.HTTP_400_BAD_REQUEST , detail = "Username or email already exit my friend")

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=security.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def read_user(user_id: int, db: Session ):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

def user_login(user:schemas.UserLogin,db:Session):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,detail = "user not found hehe"
          )
    print("Input password:", user.password)
    print("Stored hash:", db_user.hashed_password)

    result = security.verify_password(user.password,db_user.hashed_password)

    print("Verify result:", result)

    if not result:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )
   
    token_string = security.create_access_token(user_id=db_user.id)
    return schemas.Token(
        access_token=token_string,
        token_type="bearer"
        )
def create_submission(submission: schemas.Submission_schema, db: Session, current_user: models.User) -> models.Submission:
    new_submission = models.Submission(
        user_id=current_user.id,
        code=submission.code,
        language=submission.language,
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    review = service.review_code(
        new_submission.code,
        new_submission.language,
    )
    new_review = models.Review(
        submission_id=new_submission.id,
        summary=review["summary"],
        issues=review.get("issues", []),
        suggestions=review.get("suggestions", []),
        overall_score=float(review.get("overall_score", 0)),
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_submission


def get_submission(db: Session, submission_id: int, current_user: models.User) -> models.Submission | None:
    return db.query(models.Submission).filter(
        models.Submission.id == submission_id,
        models.Submission.user_id == current_user.id,
    ).first()


def get_review(db: Session, submission_id: int, current_user: models.User) -> models.Review:
    submission = db.query(models.Submission).filter(
        models.Submission.id == submission_id,
        models.Submission.user_id == current_user.id,
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found or not yours")

    review = db.query(models.Review).filter(models.Review.submission_id == submission_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return review
     