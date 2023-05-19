from fastapi import FastAPI, Depends, HTTPException, File, UploadFile   # HTTPException, File, UploadFile 추가
from sqlalchemy.orm import Session

from pydantic import BaseModel
from starlette import status   # 추가됨

import os
import crud
import schemas   # 라우터 함수 작성-> schemas 추가
from database import SessionLocal, get_db
from models import UnsolvedProblem, User
from unsolved_problem_project import get_unsolved_by_group


app = FastAPI()


@app.post("/unsolved_by_group/{group_id}")
async def save_unsolved_problems(group_id: str, db: Session = Depends(get_db)):
    unsolved_problems = get_unsolved_by_group(group_id)
    for problem_num, problem_lev in unsolved_problems.items():
        unsolved_problem = UnsolvedProblem(problem_num=problem_num, problem_lev=problem_lev)
        db.add(unsolved_problem)
    db.commit()
    return {"message": "Unsolved problems saved successfully"}


@app.get("/unsolved_by_HUFS/")
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


# 데이터 명세 5 - POST 회원가입
@app.post("/create_user/", status_code=status.HTTP_204_NO_CONTENT)
async def user_create(_user_create: schemas.UserCreate, _user_img: UploadFile, db: Session = Depends(get_db)):
    UPLOAD_DIR = "./images"   # 이미지를 저장할 서버 경로
    content = await _user_img.read()
    filename = f"{_user_create.user_id}"
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        fp.write(content)

    user = crud.get_existing_user(db, user_create=_user_create, user_img=filename)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="이미 존재하는 사용자입니다.")
    crud.create_user(db=db, user_create=_user_create)


# 데이터 명세 7 - GET 마이페이지
@app.get("/my_page/read/")
async def get_my_page(db: Session = Depends(get_db)):
    my_page = crud.get_my_page(db)
    return my_page


# 데이터 명세 7 - PUT 마이페이지(닉네임
@app.put("/my_page/update/name/", status_code=status.HTTP_204_NO_CONTENT)
async def update_my_page_name(_user_update: schemas.UserUpdateName, db: Session = Depends(get_db)):
    db_user = crud.get_one_user_info(db)
    crud.update_my_page_name(db=db, db_user=db_user, user_update=_user_update)


# 데이터 명세 7 - PUT 마이페이지(비밀번호)
@app.put("/my_page/update/password/", status_code=status.HTTP_204_NO_CONTENT)
async def update_my_page_password(_user_update: schemas.UserUpdatePw, db: Session = Depends(get_db)):
    db_user = crud.get_one_user_info(db)
    crud.update_my_page_pw(db=db, db_user=db_user, user_update=_user_update)
