from passlib.context import CryptContext
from models import UnsolvedProblem, Rank, User
from sqlalchemy.orm import Session
import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


# 데이터 명세 5 - POST 회원가입(작성중)
def create_user(db: Session, user_create=schemas.UserCreate):
    db_user = User(user_id=user_create.user_id, user_pw=pwd_context.hash(user_create.user_pw),
                   user_name=user_create.user_name)
    db.add(db_user)
    db.commit()


def get_user_by_id(db: Session, user_id: schemas.UserCreateCheckId):
    return db.query(User).filter(User.user_id == user_id.user_id).first()


def get_user_by_name(db: Session, user_name: schemas.UserCreateCheckName):
    return db.query(User).filter(User.user_name == user_name.user_name).first()


