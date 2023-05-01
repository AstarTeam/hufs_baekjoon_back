from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Unsolved_Problem(Base):
    __tablename__ = "UnsolvedProblem"

    id = Column(Integer, primary_key=True)
    problem_num = Column(Integer, nullable=False)
    problem_lev = Column(Integer, nullable=False)
