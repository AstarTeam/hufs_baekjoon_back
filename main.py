from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from pydantic import BaseModel

from database import SessionLocal, get_db
from models import UnsolvedProblem, User
from unsolved_problem_project import get_unsolved_by_group

import crud
import schemas

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


# 데이터 명세 5. POST 회원가입
@app.post("/user_create/", status_code=status.HTTP_204_NO_CONTENT)
def user_create(_user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_existing_user(db, user_create=_user_create)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다.")
    crud.create_user(db=db, user_create=_user_create)
