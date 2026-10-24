from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Text
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    submissions = relationship("Submission", back_populates="user")


class Submission(Base):
    __tablename__ = "submission"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    repo_url = Column(String, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    # New status tracking fields
    status = Column(String, nullable=False, default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)

    user = relationship("User", back_populates="submissions")
    review = relationship("Review", back_populates="submission", uselist=False)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submission.id"))

    summary = Column(Text)
    issues = Column(JSON)
    suggestions = Column(JSON)
    overall_score = Column(Float)
    metrics = Column(JSON, default=list)
    roadmap = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("Submission", back_populates="review")
    
