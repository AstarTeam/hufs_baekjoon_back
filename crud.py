from passlib.context import CryptContext
from models import UnsolvedProblem, Rank, User
import schemas  # 데이터 명세 5 - 회원가입
from sqlalchemy.orm import Session
from random import *

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 1. GET 홈페이지 - 문제 리스트 기능
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


# 3. GET 홈페이지 - 순위 기능
def get_ranking_info(db: Session):
    ranking_info = db.query(Rank).all()
    return ranking_info


def get_user_info(db: Session):   # 전체 유저 정보 반환
    user_info = db.query(User).all()
    return user_info


def get_one_user_info(db: Session, user_id: str):   # 특정 유저 정보 반환
    user_info = db.query(User).filter(User.user_id == user_id).first()
    return user_info


# 데이터 명세 5 - POST 회원가입(작성중)
def create_user(db: Session, user_create=schemas.UserCreate):
    db_user = User(user_id=user_create.user_id, user_pw=pwd_context.hash(user_create.user_pw),
                   user_name=user_create.user_name, user_baekjoon_id=user_create.user_baekjoon_id,
                   user_rand=user_create.user_rand)

    db.add(db_user)
    db.commit()


# 데이터 명세 5 - GET 회원가입: 아이디 중복 확인
def get_existing_user(db: Session, user_create: schemas.UserCreate):
    return db.query(User).filter(
        (User.username == user_create.username) |
        (User.user_baekjoon_id == user_create.user_baekjoon_id)
    ).first()


# 데이터 명세 7 - GET 마이페이지
def get_my_page(db: Session):
    my_page = db.query(User.user_id, User.user_name, User.user_solved_count, User.user_rank).all()
    return my_page


# 데이터 명세 7 - PUT 마이페이지(닉네임)
# 만약 name이나 pw 중 하나만 바꾼다면, 나머지 하나는 None이 되어버리기 때문에 프론트에서 기존의 값을 넣어줘야 함
    # name만 바꾼다면, name은 변경 값을 보내고, pw는 기존의 pw를 그대로 보내줘야함
def update_my_page_name(db: Session, db_user: User, user_update: schemas.UserUpdateName):
    db_user.name = user_update.user_name
    db.add(db_user)
    db.commit()


# 데이터 명세 7 - PUT 마이페이지(비밀번호)
def update_my_page_pw(db: Session, db_user: User, user_update: schemas.UserUpdatePw):
    db_user.user_pw = pwd_context.hash(user_update.user_pw)
    db.add(db_user)
    db.commit()


# 데이터 명세 9 - GET 마이페이지(백준 인증) - 난수 생성 및 반환
def get_rand(db: Session, db_user: User):
    rand = randint(100000, 999999)
    db_user.user_rand = rand
    db.add(db_user)
    db.commit()
    return rand
