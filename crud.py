from models import UnsolvedProblem, Rank, User
from sqlalchemy.orm import Session


def get_unsolved_problems(db: Session, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem)

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    return total, problem_list


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


def get_problem_list_ordered_by_challengers(db: Session, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).order_by(UnsolvedProblem.problem_challengers.asc())

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    return total, problem_list


def get_problem_list_ordered_by_challengers_desc(db: Session, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).order_by(UnsolvedProblem.problem_challengers.desc())

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    return total, problem_list


def get_ranking_info(db: Session):
    ranking_info = db.query(Rank).all()
    return ranking_info


def get_user_info(db: Session):
    user_info = db.query(User).all()
    return user_info
