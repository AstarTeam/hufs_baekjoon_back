from datetime import timedelta, datetime

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import BaseModel

import os
import crud
import schemas   # 라우터 함수 작성-> schemas 추가
from crud import pwd_context
from database import SessionLocal, get_db
from models import UnsolvedProblem, User
from unsolved_problem_project import get_unsolved_by_group

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = "4ab2fce7a6bd79e1c014396315ed322dd6edb1c5d975c6b74a2904135172c03c"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

app = FastAPI()


@app.post("/unsolved_by_group/{group_id}")
async def save_unsolved_problems(group_id: str, db: Session = Depends(get_db)):
    unsolved_problems = get_unsolved_by_group(group_id)
    for problem_num, problem_lev in unsolved_problems.items():
        unsolved_problem = UnsolvedProblem(problem_num=problem_num, problem_lev=problem_lev)
        db.add(unsolved_problem)
    db.commit()
    return {"message": "Unsolved problems saved successfully"}


@app.get("/unsolved_by_HUFS/")  # <- 괄호 안 url 문자열은 예시임
async def get_unsolved_problems(db: Session = Depends(get_db), page: int = 0, size: int = 15):  # 안 푼 문제 반환
    total, _problem_list = crud.get_unsolved_problems(db, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


@app.get("/problem_list_ordered_by_lev/")
async def get_problem_list_ordered_by_lev(db: Session = Depends(get_db), page: int = 0, size: int = 15):
    total, _problem_list = crud.get_problem_list_ordered_by_lev(db, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


@app.get("/problem_list_ordered_by_lev_desc/")
async def get_problem_list_ordered_by_lev_desc(db: Session = Depends(get_db), page: int = 0, size: int = 15):
    total, _problem_list = crud.get_problem_list_ordered_by_lev_desc(db, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


@app.get("/problem_list_ordered_by_challengers/")
async def get_problem_list_ordered_by_challengers(db: Session = Depends(get_db), page: int = 0, size: int = 15):
    total, _problem_list = crud.get_problem_list_ordered_by_challengers(db, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


@app.get("/problem_list_ordered_by_challengers_desc/")
async def get_problem_list_ordered_by_challengers_desc(db: Session = Depends(get_db), page: int = 0, size: int = 15):
    total, _problem_list = crud.get_problem_list_ordered_by_challengers_desc(db, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


@app.get("/ranking_info/")
async def get_ranking_info(db: Session = Depends(get_db)):
    ranking_info = crud.get_ranking_info(db)
    return ranking_info


@app.get("/user_info/")
async def get_user_info(db: Session = Depends(get_db)):
    user_info = crud.get_user_info(db)
    return user_info


# 데이터 명세 4 - GET 홈페이지 - 명예의 전당
@app.get("/fame/")
async def get_fame(db: Session = Depends(get_db)):
    fame = crud.read_fame(db)
    return fame


# 데이터 명세 5. POST 회원가입 - 아이디 중복 확인
@app.post("/user_create/user_id_check/")
def user_id_check(_user_id: schemas.UserCreateCheckId, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id=_user_id)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다.")
    return {"message": "사용 가능한 아이디입니다."}


# 데이터 명세 5. POST 회원가입 - 이름 중복 확인
@app.post("/user_create/user_name_check/")
def user_name_check(_user_name: schemas.UserCreateCheckName, db: Session = Depends(get_db)):
    user = crud.get_user_by_name(db, user_name=_user_name)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다.")
    return {"message": "사용 가능한 이름입니다."}


# 데이터 명세 5. POST 회원가입
@app.post("/user_create/join/")
def user_create(_user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    crud.create_user(db=db, user_create=_user_create)
    return {"message": "회원가입이 완료되었습니다."}


# 데이터 명세 6. POST 로그인
@app.post("/login/", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):

    # check user and password
    user = crud.get_user(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.user_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 잘못되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # make access token
    data = {
        "sub": user.user_id,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "user_auth": user.user_auth
    }


# 헤더 정보의 토큰값 읽어서 사용자 객체를 리턴
def get_current_user(token: str = Depends(oauth2_scheme),
                     db:Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 토큰입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = crud.get_user(db, user_id=user_id)
        if user is None:
            raise credentials_exception
    return user


# 데이터 명세 7 - GET 마이페이지
@app.get("/my_page/read/")
async def get_my_page(db: Session = Depends(get_db)):
    my_page = crud.get_my_page(db)
    return my_page


# 데이터 명세 7 - PUT 마이페이지(닉네임)
@app.put("/my_page/update/name/", status_code=status.HTTP_204_NO_CONTENT)
async def update_my_page_name(_user_update: schemas.UserUpdateName, db: Session = Depends(get_db)):
    db_user = crud.get_one_user_info(db)
    crud.update_my_page_name(db=db, db_user=db_user, user_update=_user_update)


# 데이터 명세 7 - PUT 마이페이지(비밀번호)
@app.put("/my_page/update/password/", status_code=status.HTTP_204_NO_CONTENT)
async def update_my_page_password(_user_update: schemas.UserUpdatePw, db: Session = Depends(get_db)):
    db_user = crud.get_one_user_info(db)
    crud.update_my_page_pw(db=db, db_user=db_user, user_update=_user_update)

