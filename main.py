from datetime import timedelta, datetime

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import crud
import schemas
from crud import pwd_context
from database import SessionLocal, get_db
from models import UnsolvedProblem, User, Challengers
from unsolved_problem_project import get_unsolved_by_group

from apscheduler.schedulers.background import BackgroundScheduler

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = "4ab2fce7a6bd79e1c014396315ed322dd6edb1c5d975c6b74a2904135172c03c"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/unsolved-by-HUFS")
async def get_unsolved_problems(db: Session = Depends(get_db), page: int = 0, size: int = 15):  # 안 푼 문제 반환
    total, _problem_list = crud.read_unsolved_problems(db, user_id=None, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


@app.get("/unsolved-by-HUFS/token")
async def get_unsolved_problems_token(db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
                                      page: int = 0, size: int = 15):  # 안 푼 문제 반환
    total, _problem_list = crud.read_unsolved_problems(db, user_id=current_user.user_id, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


@app.get("/problem-list-ordered-by-lev")
async def get_problem_list_ordered_by_lev(db: Session = Depends(get_db), page: int = 0, size: int = 15):
    total, _problem_list = crud.read_problem_list_ordered_by_lev(db, user_id=None, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


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


@app.get("/problem-list-ordered-by-lev-desc")
async def get_problem_list_ordered_by_lev_desc(db: Session = Depends(get_db), page: int = 0, size: int = 15):
    total, _problem_list = crud.read_problem_list_ordered_by_lev_desc(db, user_id=None, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


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


@app.get("/problem-list-ordered-by-challengers")
async def get_problem_list_ordered_by_challengers(db: Session = Depends(get_db), page: int = 0, size: int = 15):
    total, _problem_list = crud.read_problem_list_ordered_by_challengers(db, user_id=None, skip=page * size, limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


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


@app.get("/problem-list-ordered-by-challengers-desc")
async def get_problem_list_ordered_by_challengers_desc(db: Session = Depends(get_db), page: int = 0, size: int = 15):
    total, _problem_list = crud.read_problem_list_ordered_by_challengers_desc(db, user_id=None, skip=page * size,
                                                                              limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


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


@app.get("/problem-list-challenging/token")
async def get_problem_list_challenging(db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
                                       page: int = 0, size: int = 15):
    total, _problem_list = crud.read_problem_list_challenging(db, user_id=current_user.user_id, skip=page * size,
                                                              limit=size)
    return {
        "total": total,
        "problem_list": _problem_list
    }


@app.get("/problem-list-not-challenged/token")
async def get_problem_list_not_challenged(db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
                                          page: int = 0, size: int = 15):
    total, _problem_list = crud.read_problem_list_not_challenged(db, user_id=current_user.user_id, skip=page * size,
                                                                 limit=size)
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


@app.get("/fame")
async def get_fame(db: Session = Depends(get_db)):
    fame = crud.read_fame(db)
    return {"userList": fame}


@app.get("/user-create/user-id-check/{user_id}")
def user_id_check(user_id: str, db: Session = Depends(get_db)):
    user = crud.read_user_by_id(db, user_id=user_id)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다.")
    return {"message": "사용 가능한 아이디입니다."}


@app.get("/user-create/user-name-check/{user_name}")
def user_name_check(user_name: str, db: Session = Depends(get_db)):
    user = crud.read_user_by_name(db, user_name=user_name)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다.")
    return {"message": "사용 가능한 이름입니다."}


@app.post("/user-create/join")
def user_create(_user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    crud.create_user(db=db, user_create=_user_create)
    return {"message": "회원가입이 완료되었습니다."}


@app.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    user = crud.read_user(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.user_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 잘못되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

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


@app.get("/my-page/read")
async def get_my_page(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다.")
    my_page = crud.read_my_page(db, db_user=current_user)
    return my_page


@app.put("/my-page/update/name")
async def update_my_page_name(_update_name: str, db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    crud.update_my_page_name(db=db, db_user=current_user, user_update=_update_name)
    return {"message": "닉네임이 변경되었습니다."}


@app.put("/my-page/update/password")
async def update_my_page_password(_update_pw: str, db: Session = Depends(get_db),
                                  current_user: User = Depends(get_current_user)):
    crud.update_my_page_pw(db=db, db_user=current_user, user_update=_update_pw)
    return {"message": "비밀번호가 변경되었습니다."}


@app.delete("/my-page/delete")
async def delete_my_page(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    crud.delete_my_page(db=db, db_user=current_user)
    return {"message": "회원탈퇴가 완료되었습니다."}


@app.get("/my-page/rand/{user_id}")
async def get_my_page_rand(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rand = crud.read_random_number(db=db, user_id=current_user.user_id)
    return rand


@app.post("/my-page/auth")
async def post_my_page_auth(file: UploadFile, boj_id: str, current_user: User = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    UPLOAD_DIR = "./photo"

    content = await file.read()
    filename = f"{current_user.user_id}.jpg"
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        fp.write(content)

    crud.update_my_page_auth(db=db, db_user=current_user, boj_id=boj_id)
    return {"message": "인증 신청이 완료되었습니다."}


@app.get("/search")
async def get_search(problem_num: str, db: Session = Depends(get_db)):
    search = crud.read_search(db, problem_num=problem_num, user_id=None)
    if search:
        return search
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="문제를 찾을 수 없습니다.")


@app.get("/search/token")
async def get_search_token(problem_num: str, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    search = crud.read_search(db, problem_num=problem_num, user_id=current_user.user_id)
    if search:
        return search
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="문제를 찾을 수 없습니다.")


@app.get("/recommend")
async def get_recommend(db: Session = Depends(get_db)):
    recommend = crud.read_recommend(db)
    return recommend


def update_recommend():
    crud.update_recommend()


@app.post("/problem/challenge/{problem_num}")
def challenge_problem(problem_num: int, current_user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    challenger = db.query(Challengers).filter(
        Challengers.challenge_problem == problem_num,
        Challengers.challenger_id == current_user.user_id).first()
    if challenger == None:
        new_challenge = Challengers(challenger_id=current_user.user_id, challenge_problem=problem_num)
        db.add(new_challenge)
        problem = db.query(UnsolvedProblem).filter(UnsolvedProblem.problem_num == problem_num).first()
        problem.problem_challengers += 1
        db.commit()
        return {"message": "도전자 +."}
    else:
        return {"message": "challenger already on table"}


@app.post("/problem/unchallenge/{problem_num}")
def unchallenge_problem(problem_num: int, current_user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    unchallenge = db.query(Challengers).filter(
        Challengers.challenge_problem == problem_num,
        Challengers.challenger_id == current_user.user_id).first()
    if unchallenge != None:
        db.delete(unchallenge)
        problem = db.query(UnsolvedProblem).filter(UnsolvedProblem.problem_num == problem_num).first()
        problem.problem_challengers -= 1
        db.commit()
        return {"message": "도전자 -."}
    else:
        return {"message": "challenger not on table"}


scheduler = BackgroundScheduler()
scheduler.add_job(update_recommend, 'cron', hour=0)
scheduler.start()
