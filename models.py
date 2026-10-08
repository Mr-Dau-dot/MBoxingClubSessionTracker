import datetime
from flask_login import UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, Boolean, DateTime, Time, Date
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, foreign
from flask import Flask

db = SQLAlchemy()
class User(UserMixin,db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String,nullable=False)
    email: Mapped[str] = mapped_column(String,unique=True,nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    join_date: Mapped[datetime] = mapped_column(DateTime,default=datetime.datetime.today, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean,default=True, nullable=False)
    session_as_coach = relationship("TrainingSession", foreign_keys="TrainingSession.coach_id",
                                    back_populates="coach")
    session_as_member = relationship("TrainingSession", foreign_keys="TrainingSession.member_id",
                                     back_populates="member")
    member_package = relationship("Package",foreign_keys="Package.member_id",back_populates="member")
    coach_package = relationship("Package", foreign_keys="Package.coach_id",back_populates="coach")

class TrainingSession(db.Model):
    __tablename__ = "training_session"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date,default=datetime.date.today,nullable=False)
    start_time: Mapped[datetime] = mapped_column(Time,nullable=False)
    end_time: Mapped[datetime] = mapped_column(Time,nullable=False)
    session_type: Mapped[str] = mapped_column(String,nullable=True)
    session_status: Mapped[str] = mapped_column(String,default="scheduled",nullable=False)
    notes: Mapped[str] = mapped_column(String,nullable=True)

    coach_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"), nullable=False)
    member_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"), nullable=False)
    coach = relationship("User", foreign_keys=[coach_id], back_populates="session_as_coach")
    member = relationship("User", foreign_keys=[member_id], back_populates="session_as_member")

    package_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("package.id"), nullable=False)
    package = relationship("Package",back_populates="sessions")

class Package(db.Model):
    __tablename__ = "package"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    package_name: Mapped[str] = mapped_column(String,nullable=False)
    package_starting_date: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today,nullable=False)
    number_of_session: Mapped[int] = mapped_column(Integer,nullable=False)
    member_id: Mapped[int] = mapped_column(Integer,db.ForeignKey("users.id"),nullable=False)
    coach_id: Mapped[int] = mapped_column(Integer,db.ForeignKey("users.id"),nullable=False)
    member = relationship("User",foreign_keys=[member_id],back_populates="member_package")
    coach = relationship("User",foreign_keys=[coach_id],back_populates="coach_package")
    sessions = relationship("TrainingSession",back_populates="package")
