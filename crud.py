from passlib.context import CryptContext
from models import UnsolvedProblem, Rank, User
import schemas
from sqlalchemy.orm import Session
from random import randint


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_unsolved_problems(db: Session, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem)

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    return total, problem_list


def read_problem_list_ordered_by_lev(db: Session, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).order_by(UnsolvedProblem.problem_lev.asc())

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    return total, problem_list


def read_problem_list_ordered_by_lev_desc(db: Session, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).order_by(UnsolvedProblem.problem_lev.desc())

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    return total, problem_list


def read_problem_list_ordered_by_challengers(db: Session, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).order_by(UnsolvedProblem.problem_challengers.asc())

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    return total, problem_list


def read_problem_list_ordered_by_challengers_desc(db: Session, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).order_by(UnsolvedProblem.problem_challengers.desc())

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    return total, problem_list


def read_ranking_info(db: Session):
    ranking_info = db.query(Rank).all()
    return ranking_info


def read_user_info(db: Session):
    user_info = db.query(User).all()
    return user_info


# 데이터 명세 4 - GET 홈페이지 - 명예의 전당
def read_fame(db: Session, limit: int = 10):
    result = db.query(User.user_name, User.user_solved_count).filter(User.user_name.isnot(None))\
        .filter(User.user_solved_count.isnot(None)).order_by(User.user_solved_count.desc()).limit(limit).all()
    return [{"name": user_id, "count": user_solved_count} for user_id, user_solved_count in result]


# 데이터 명세 5 - POST 회원가입(작성중)
def create_user(db: Session, user_create=schemas.UserCreate):
    rand = randint(100000, 999999)
    db_user = User(user_id=user_create.user_id, user_pw=pwd_context.hash(user_create.user_pw),
                   user_name=user_create.user_name, user_solved_count=0, user_auth=0, user_rand=rand)
    db.add(db_user)
    db.commit()


def read_user(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()


def read_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()


def read_user_by_name(db: Session, user_name: str):
    return db.query(User).filter(User.user_name == user_name).first()


# 데이터 명세 7 - GET 마이페이지
def read_my_page(db: Session):
    my_page = db.query(User.user_id, User.user_name, User.user_solved_count, User.user_rank).all()
    return my_page


# 데이터 명세 7 - PUT 마이페이지(닉네임)
def update_my_page_name(db: Session, db_user: User, user_update: str):
    db_user.user_name = user_update
    db.add(db_user)
    db.commit()


# 데이터 명세 7 - PUT 마이페이지(비밀번호)
def update_my_page_pw(db: Session, db_user: User, user_update: str):
    db_user.user_pw = pwd_context.hash(user_update)
    db.add(db_user)
    db.commit()


# 데이터 명세 8 - GET 백준 인증 - 난수 받기
def read_random_number(db: Session, user_id: str):
    result = db.query(User.user_rand).filter(User.user_rand.isnot(None)).filter(User.user_id == user_id).first()
    return {"rand": user_rand for user_rand in result}


def update_my_page_auth(db: Session, db_user: User, boj_id: str):
    db_user.user_auth = 2
    db_user.user_boj_id = boj_id
    db.add(db_user)
    db.commit()
