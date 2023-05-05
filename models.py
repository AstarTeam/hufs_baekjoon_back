from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class UnsolvedProblem(Base):
    __tablename__ = "UnsolvedProblem"

    problem_num = Column(Integer, nullable=False)
    problem_title = Column(String(255), index=True)
    problem_lev = Column(Integer, nullable=False)


class User(Base):
    __tablename__ = "User"

    user_id = Column(String(255), index=True)
    user_pw = Column(String(255), index=True)
    user_name = Column(String(255), primary_key=True)
    user_solved_count = Column(Integer, nullable=False)
    user_baekjoon_id = Column(String(255), nullable=False)
