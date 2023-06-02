from random import randint

from passlib.context import CryptContext
from sqlalchemy.orm import Session

import schemas
import unsolved_problem_project
from database import SessionLocal
from models import UnsolvedProblem, Rank, User, Challengers, Recommend

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def is_user_challenged(db: Session, user_id: str, problem_num: int):
    return True if db.query(Challengers).filter(Challengers.challenger_id == user_id,
                                                Challengers.challenge_problem == problem_num).first() else False


def make_problem_list(db, user_id, _problem_list):
    problem_list = [{"problem_link": problem.problem_link, "problem_challengers": problem.problem_challengers,
                     "problem_lev": problem.problem_lev, "problem_num": problem.problem_num,
                     "problem_title": problem.problem_title,
                     "is_user_challenged": is_user_challenged(db, user_id, problem.problem_num)}
                    for problem in _problem_list]
    return problem_list


def read_unsolved_problems(db: Session, user_id: str, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem)

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    if user_id:
        problem_list = make_problem_list(db, user_id, problem_list)
    return total, problem_list


def read_problem_list_ordered_by_lev(db: Session, user_id: str, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).order_by(UnsolvedProblem.problem_lev.asc())

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    if user_id:
        problem_list = make_problem_list(db, user_id, problem_list)
    return total, problem_list


def read_problem_list_ordered_by_lev_desc(db: Session, user_id: str, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).order_by(UnsolvedProblem.problem_lev.desc())

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    if user_id:
        problem_list = make_problem_list(db, user_id, problem_list)
    return total, problem_list


def read_problem_list_ordered_by_challengers(db: Session, user_id: str, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).order_by(UnsolvedProblem.problem_challengers.asc())

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    if user_id:
        problem_list = make_problem_list(db, user_id, problem_list)
    return total, problem_list


def read_problem_list_ordered_by_challengers_desc(db: Session, user_id: str, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).order_by(UnsolvedProblem.problem_challengers.desc())

    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    if user_id:
        problem_list = make_problem_list(db, user_id, problem_list)
    return total, problem_list


# 데이터 명세 2.5 - GET 홈페이지 - 문제 정렬 기능 - 도전 중인 문제
def read_problem_list_challenging(db: Session, user_id: str, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).filter(UnsolvedProblem.problem_num
                                                     .in_(db.query(Challengers.challenge_problem)
                                                          .filter(Challengers.challenger_id == user_id)))
    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    problem_list = make_problem_list(db, user_id, problem_list)
    return total, problem_list


# 데이터 명세 2.6 - GET 홈페이지 - 문제 정렬 기능 - 안 푼 문제
def read_problem_list_not_challenged(db: Session, user_id: str, skip: int = 0, limit: int = 15):
    _problem_list = db.query(UnsolvedProblem).filter(UnsolvedProblem.problem_num
                                                     .notin_(db.query(Challengers.challenge_problem)
                                                             .filter(Challengers.challenger_id == user_id)))
    total = _problem_list.count()
    problem_list = _problem_list.offset(skip).limit(limit).all()
    problem_list = make_problem_list(db, user_id, problem_list)
    return total, problem_list


def read_ranking_info(db: Session):
    ranking_info = db.query(Rank).all()
    return ranking_info


def read_user_info(db: Session):
    user_info = db.query(User).all()
    return user_info


# 데이터 명세 4 - GET 홈페이지 - 명예의 전당
def read_fame(db: Session, limit: int = 10):
    result = db.query(User.user_name, User.user_solved_count).filter(User.user_name.isnot(None)) \
        .filter(User.user_solved_count.isnot(None)).order_by(User.user_solved_count.desc()).limit(limit).all()
    return [{"name": user_id, "count": user_solved_count} for user_id, user_solved_count in result]


# 데이터 명세 5 - POST 회원가입(작성중)
def create_user(db: Session, user_create=schemas.UserCreate):
    rand = randint(100000, 999999)
    db_user = User(user_id=user_create.user_id, user_pw=pwd_context.hash(user_create.user_pw),
                   user_name=user_create.user_name, user_solved_count=0, user_auth=0, user_rand=rand)
    db.add(db_user)
    db.commit()
    unsolved_problem_project.update_user_rank(405)


def read_user(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()


def read_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()


def read_user_by_name(db: Session, user_name: str):
    return db.query(User).filter(User.user_name == user_name).first()


# 데이터 명세 7 - GET 마이페이지
def read_my_page(db: Session, db_user: User):
    unsolved_problem_project.update_user_rank(405)
    if db_user.user_auth == 1:
        my_page = db.query(User.user_id, User.user_name, User.user_solved_count, User.user_rank,
                           User.user_baekjoon_id).filter(User.user_id.isnot(None)) \
            .filter(User.user_name.isnot(None)).filter(User.user_solved_count.isnot(None)) \
            .filter(User.user_rank.isnot(None)).filter(User.user_baekjoon_id.isnot(None)) \
            .filter(User.user_id == db_user.user_id).first()
        return {"user_id": my_page[0], "user_name": my_page[1], "user_solved_count": my_page[2],
                "user_rank": my_page[3], "user_baekjoon_id": my_page[4]}
    else:
        my_page = db.query(User.user_id, User.user_name, User.user_solved_count, User.user_rank) \
            .filter(User.user_id.isnot(None)).filter(User.user_name.isnot(None)) \
            .filter(User.user_solved_count.isnot(None)).filter(User.user_id == db_user.user_id).first()
        return {"user_id": my_page[0], "user_name": my_page[1], "user_solved_count": my_page[2]}


# 데이터 명세 8.1 - PUT 마이페이지(닉네임)
def update_my_page_name(db: Session, db_user: User, user_update: str):
    db_user.user_name = user_update
    db.add(db_user)
    db.commit()


# 데이터 명세 8.2 - PUT 마이페이지(비밀번호)
def update_my_page_pw(db: Session, db_user: User, user_update: str):
    db_user.user_pw = pwd_context.hash(user_update)
    db.add(db_user)
    db.commit()


# 데이터 명세 8.3 - DELETE 마이페이지
def delete_my_page(db: Session, db_user: User):
    _user = db.query(Challengers).filter(Challengers.challenger_id == db_user.user_id).all()
    for user in _user:
        db.delete(user)
    db.delete(db_user)
    db.commit()


# 데이터 명세 9 - GET 백준 인증 - 난수 받기
def read_random_number(db: Session, user_id: str):
    result = db.query(User.user_rand).filter(User.user_rand.isnot(None)).filter(User.user_id == user_id).first()
    return {"rand": user_rand for user_rand in result}


def update_my_page_auth(db: Session, db_user: User, boj_id: str):
    db_user.user_auth = 2
    db_user.user_boj_id = boj_id
    db.add(db_user)
    db.commit()


# 데이터 명세 11.2 - GET 홈페이지 - 검색(로그인 했을 때)
def read_search(db: Session, user_id: str, problem_num: str):
    result = db.query(UnsolvedProblem).filter(UnsolvedProblem.problem_num == problem_num).first()
    if result:
        if user_id:
            return make_problem_list(db, user_id, {result})
        else:
            return result


def update_recommend():
    db = SessionLocal()
    bronze, silver, gold, platinum, diamond, ruby = False, False, False, False, False, False
    while (bronze, silver, gold, platinum, diamond, ruby) != (True, True, True, True, True, True):
        num = randint(1000, 30000)
        result = db.query(UnsolvedProblem).filter(UnsolvedProblem.problem_num == num).first()
        flag = None
        if result:
            if 1 <= result.problem_lev <= 5 and not bronze:
                bronze = True
                flag = "bronze"
            elif 6 <= result.problem_lev <= 10 and not silver:
                silver = True
                flag = "silver"
            elif 11 <= result.problem_lev <= 15 and not gold:
                gold = True
                flag = "gold"
            elif 16 <= result.problem_lev <= 20 and not platinum:
                platinum = True
                flag = "platinum"
            elif 21 <= result.problem_lev <= 25 and not diamond:
                diamond = True
                flag = "diamond"
            elif 26 <= result.problem_lev <= 30 and not ruby:
                ruby = True
                flag = "ruby"
            else:
                continue
            _db_update = db.query(Recommend).filter(Recommend.id == flag).first()
            _db_update.problem_num, _db_update.problem_title, _db_update.problem_lev, _db_update.problem_link = \
                result.problem_num, result.problem_title, result.problem_lev, result.problem_link
            db.add(_db_update)
            db.commit()
    db.close()


# 데이터 명세 12 - GET 추천 문제 가져오기
def read_recommend(db: Session):
    result = db.query(Recommend).all()
    return result
