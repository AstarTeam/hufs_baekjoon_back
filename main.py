import uuid
from datetime import timedelta, datetime

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import BaseModel

import os
import crud
import schemas  # 라우터 함수 작성-> schemas 추가
from crud import pwd_context
from database import SessionLocal, get_db
from models import UnsolvedProblem, User
from unsolved_problem_project import get_unsolved_by_group

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = "4ab2fce7a6bd79e1c014396315ed322dd6edb1c5d975c6b74a2904135172c03c"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

app = FastAPI()


# 헤더 정보의 토큰값 읽어서 사용자 객체를 리턴
def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
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
        user = crud.read_user(db, user_id=user_id)
        if user is None:
            raise credentials_exception
    return user


@app.post("/unsolved_by_group/{group_id}")
async def save_unsolved_problems(group_id: str, db: Session = Depends(get_db)):
    unsolved_problems = get_unsolved_by_group(group_id)
    for problem_num, problem_lev in unsolved_problems.items():
        unsolved_problem = UnsolvedProblem(problem_num=problem_num, problem_lev=problem_lev)
        db.add(unsolved_problem)
    db.commit()
    return {"message": "Unsolved problems saved successfully"}


# 데이터 명세 1.1 - GET 홈페이지 - 문제 리스트 기능(로그인 안 했을 때)
@app.get("/unsolved-by-HUFS")
async def get_unsolved_problems(db: Session = Depends(get_db), page: int = 0, size: int = 15):  # 안 푼 문제 반환
    total, _problem_list = crud.read_unsolved_problems(db, user_id=1234, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


# 데이터 명세 1.2 - GET 홈페이지 - 문제 리스트 기능(로그인 했을 때)
@app.get("/unsolved-by-HUFS/token")
async def get_unsolved_problems_token(db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
                                      page: int = 0, size: int = 15):  # 안 푼 문제 반환
    total, _problem_list = crud.read_unsolved_problems(db, user_id=current_user.user_id, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


# 데이터 명세 2.1.1 - GET 홈페이지 - 문제 정렬 기능 - GET 쉬운 순 정렬(로그인 안 했을 때)
@app.get("/problem-list-ordered-by-lev")
async def get_problem_list_ordered_by_lev(db: Session = Depends(get_db), page: int = 0, size: int = 15):
    total, _problem_list = crud.read_problem_list_ordered_by_lev(db, user_id=1234, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


# 데이터 명세 2.1.2 - GET 홈페이지 - 문제 정렬 기능 - GET 쉬운 순 정렬(로그인 했을 때)
@app.get("/problem-list-ordered-by-lev/token")
async def get_problem_list_ordered_by_lev_token(db: Session = Depends(get_db),
                                                current_user: User = Depends(get_current_user),
                                                page: int = 0, size: int = 15):
    total, _problem_list = crud.read_problem_list_ordered_by_lev(db, user_id=current_user.user_id, skip=page * size,
                                                                 limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


# 데이터 명세 2.2.1 - GET 홈페이지 - 문제 정렬 기능 - GET 어려운 순 정렬(로그인 안 했을 때)
@app.get("/problem-list-ordered-by-lev-desc")
async def get_problem_list_ordered_by_lev_desc(db: Session = Depends(get_db), page: int = 0, size: int = 15):
    total, _problem_list = crud.read_problem_list_ordered_by_lev_desc(db, user_id=1234, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


# 데이터 명세 2.2.2 - GET 홈페이지 - 문제 정렬 기능 - GET 어려운 순 정렬(로그인 했을 때)
@app.get("/problem-list-ordered-by-lev-desc/token")
async def get_problem_list_ordered_by_lev_desc_token(db: Session = Depends(get_db),
                                                     current_user: User = Depends(get_current_user), page: int = 0,
                                                     size: int = 15):
    total, _problem_list = crud.read_problem_list_ordered_by_lev_desc(db, user_id=current_user.user_id,
                                                                      skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


# 데이터 명세 2.3.1 - GET 홈페이지 - 문제 정렬 기능 - GET 도전자 많은 순 정렬(로그인 안 했을 때)
@app.get("/problem-list-ordered-by-challengers")
async def get_problem_list_ordered_by_challengers(db: Session = Depends(get_db), page: int = 0, size: int = 15):
    total, _problem_list = crud.read_problem_list_ordered_by_challengers(db, user_id=1234, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


# 데이터 명세 2.3.2 - GET 홈페이지 - 문제 정렬 기능 - GET 도전자 많은 순 정렬(로그인 했을 때)
@app.get("/problem-list-ordered-by-challengers/token")
async def get_problem_list_ordered_by_challengers_token(db: Session = Depends(get_db),
                                                        current_user: User = Depends(get_current_user), page: int = 0,
                                                        size: int = 15):
    total, _problem_list = crud.read_problem_list_ordered_by_challengers(db, user_id=current_user.user_id,
                                                                         skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


# 데이터 명세 2.4.1 - GET 홈페이지 - 문제 정렬 기능 - 도전자 적은 순 정렬(로그인 안 했을 때)
@app.get("/problem-list-ordered-by-challengers-desc")
async def get_problem_list_ordered_by_challengers_desc(db: Session = Depends(get_db),
                                                       current_user: User = Depends(get_current_user), page: int = 0,
                                                       size: int = 15):
    total, _problem_list = crud.read_problem_list_ordered_by_challengers_desc(db, user_id=1234, skip=page * size,
                                                                              limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


# 데이터 명세 2.4.2 - GET 홈페이지 - 문제 정렬 기능 - 도전자 적은 순 정렬(로그인 안 했을 때)
@app.get("/problem-list-ordered-by-challengers-desc/token")
async def get_problem_list_ordered_by_challengers_desc_token(db: Session = Depends(get_db),
                                                             current_user: User = Depends(get_current_user),
                                                             page: int = 0, size: int = 15):
    total, _problem_list = crud.read_problem_list_ordered_by_challengers_desc(db, user_id=current_user.user_id,
                                                                              skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


@app.get("/ranking-info")
async def get_ranking_info(db: Session = Depends(get_db)):
    ranking_info = crud.read_ranking_info(db)
    return ranking_info


@app.get("/user-info")
async def get_user_info(db: Session = Depends(get_db)):
    user_info = crud.read_user_info(db)
    return user_info


# 데이터 명세 4 - GET 홈페이지 - 명예의 전당
@app.get("/fame")
async def get_fame(db: Session = Depends(get_db)):
    fame = crud.read_fame(db)
    return {"userList": fame}


# 데이터 명세 5. 회원가입 - 아이디 중복 확인
@app.get("/user-create/user-id-check/{user_id}")
def user_id_check(user_id: str, db: Session = Depends(get_db)):
    user = crud.read_user_by_id(db, user_id=user_id)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다.")
    return {"message": "사용 가능한 아이디입니다."}


# 데이터 명세 5. 회원가입 - 닉네임 중복 확인
@app.get("/user-create/user-name-check/{user_name}")
def user_name_check(user_name: str, db: Session = Depends(get_db)):
    user = crud.read_user_by_name(db, user_name=user_name)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다.")
    return {"message": "사용 가능한 이름입니다."}


# 데이터 명세 5. 회원가입
@app.post("/user-create/join")
def user_create(_user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    crud.create_user(db=db, user_create=_user_create)
    return {"message": "회원가입이 완료되었습니다."}


# 데이터 명세 6. POST 로그인
@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    # check user and password
    user = crud.read_user(db, form_data.username)
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


# 데이터 명세 6.2 POST 로그아웃


# 데이터 명세 7 - GET 마이페이지
@app.get("/my-page/read")
async def get_my_page(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다.")
    my_page = crud.read_my_page(db, db_user=current_user)
    return my_page


# 데이터 명세 8.1 - PUT 마이페이지(닉네임)
@app.put("/my-page/update/name")
async def update_my_page_name(_update_name: str, db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    db_user = crud.read_user(db, user_id=current_user.user_id)
    crud.update_my_page_name(db=db, db_user=db_user, user_update=_update_name)
    return {"message": "닉네임이 변경되었습니다."}


# 데이터 명세 8.2 - PUT 마이페이지(비밀번호)
@app.put("/my-page/update/password")
async def update_my_page_password(_update_pw: str, db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user)):
    db_user = crud.read_user(db, user_id=current_user.user_id)
    crud.update_my_page_pw(db=db, db_user=db_user, user_update=_update_pw)
    return {"message": "비밀번호가 변경되었습니다."}


# 데이터 명세 9 - GET 백준 인증 - 난수 받기
@app.get("/my-page/rand/{user_id}")
async def get_my_page_rand(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user = crud.read_user(db, user_id=current_user.user_id)
    rand = crud.read_random_number(db=db, user_id=db_user.user_id)
    return rand


# 데이터 명세 10 - POST 백준 인증
@app.post("/my-page/auth")
async def post_my_page_auth(file: UploadFile, boj_id: str, current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    UPLOAD_DIR = "./photo"  # 이미지를 저장할 서버 경로

    content = await file.read()
    filename = f"{current_user.user_id}.jpg"  # uuid로 유니크한 파일명으로 변경
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        fp.write(content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    db_user = crud.read_user(db, user_id=current_user.user_id)
    crud.update_my_page_auth(db=db, db_user=db_user, boj_id=boj_id)
    return {"message": "인증 신청이 완료되었습니다."}
