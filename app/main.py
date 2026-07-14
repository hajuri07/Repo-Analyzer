# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database  import get_db,Base, engine
from app import models
from  .import schemas
from app import crud as user_crud

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import security
from fastapi import  HTTPException
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



Base.metadata.create_all(bind=engine)




@app.post("/auth/signup",response_model=schemas.UserResponse,status_code=201)
def register_user(user:schemas.UserCreate, db: Session = Depends(get_db)):
    return user_crud.create_user(db=db,user=user)


@app.get("/auth/users/{user_id}",response_model=schemas.UserResponse)

def get_user(user_id: int,db: Session = Depends(get_db)):
    return user_crud.read_user(db=db, user_id=user_id)


@app.post("/auth/login",response_model=schemas.Token)

def user_login(user:schemas.UserLogin , db:Session = Depends(get_db)):
    return user_crud.user_login(db = db, user = user)



@app.post("/submission/analyze", response_model=schemas.SubmissionResponse, status_code=201)
def user_submission(sub: schemas.SubmissionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)):
    return user_crud.create_submission(submission=sub, current_user=current_user, db=db)


@app.get("/submission/{submission_id}",response_model = schemas.SubmissionResponse)
def get_sub(submission_id:int ,db:Session = Depends(get_db),current_user: models.User = Depends(security.get_current_user)):
    result = user_crud.get_submission(db=db, submission_id=submission_id, current_user=current_user)

    if not result:
        raise HTTPException(status_code=404,detail = "Submission not found or not yours")
    return result
@app.get("/submission/{submission_id}/review",response_model=schemas.ReviewResponse)
def get_review(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    return user_crud.get_review(
        submission_id=submission_id,
        current_user=current_user,
        db=db
    )

