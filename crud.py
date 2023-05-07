from models import UnsolvedProblem, Rank, User
from sqlalchemy.orm import Session


def get_unsolved_problems(db: Session):  # 안 푼 문제 반환
    unsolved_problems = db.query(UnsolvedProblem).all()
    return unsolved_problems


def get_problem_list_ordered_by_lev(db: Session, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).order_by(UnsolvedProblem.problem_lev.asc())

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    return total, problem_list


def get_problem_list_ordered_by_lev_desc(db: Session, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).order_by(UnsolvedProblem.problem_lev.desc())

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    return total, problem_list


def get_ranking_info(db: Session):
    ranking_info = db.query(Rank).all()
    return ranking_info


def get_user_info(db: Session):
    user_info = db.query(User).all()
    return user_info