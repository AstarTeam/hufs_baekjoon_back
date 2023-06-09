from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class UnsolvedProblem(Base):
    __tablename__ = "unsolved_problem"

    problem_num = Column(Integer, primary_key=True)
    problem_title = Column(String(255), index=True)
    problem_lev = Column(Integer, nullable=False)
    problem_link = Column(String(255), nullable=False)
    problem_challengers = Column(Integer, nullable=False)


class Rank(Base):
    __tablename__ = "rank"

    hufs_rank = Column(Integer, primary_key=True)
    hufs_now_solved = Column(Integer, nullable=False)
    hufs_pre_solved = Column(Integer, nullable=True)
    high_rank_name = Column(String(255), nullable=False)
    high_rank_now_solved = Column(Integer, nullable=False)
    high_rank_pre_solved = Column(Integer, nullable=True)
    low_rank_name = Column(String(255), nullable=False)
    low_rank_now_solved = Column(Integer, nullable=False)
    low_rank_pre_solved = Column(Integer, nullable=True)


class User(Base):
    __tablename__ = "user"

    user_id = Column(String(255), primary_key=True)
    user_pw = Column(String(255), index=True)
    user_name = Column(String(255), index=True)
    user_solved_count = Column(Integer, nullable=True)
    user_baekjoon_id = Column(String(255), nullable=True)
    user_rank = Column(Integer, nullable=True)
    user_rand = Column(Integer, nullable=True)
    user_auth = Column(Integer, nullable=True)


class Challengers(Base):
    __tablename__ = "challengers"

    challenger_id = Column(String(255), primary_key=False)
    challenge_problem = Column(Integer, primary_key=False)


class Recommend(Base):
    __tablename__ = "recommend"

    id = Column(String(255), primary_key=True, index=True)
    problem_num = Column(Integer, nullable=True)
    problem_title = Column(String(255), nullable=True)
    problem_lev = Column(Integer, nullable=True)
    problem_link = Column(String(255), nullable=True)
