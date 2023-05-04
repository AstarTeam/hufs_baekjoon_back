from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from pydantic import BaseModel
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


@app.get("/unsolved_by_HUFS")  # <- 괄호 안 url 문자열은 예시임
def unsolved_problems(db: Session = Depends(get_db)):  # 안 푼 문제 반환
    get_unsolved_problems = db.query(UnsolvedProblem).all()
    return get_unsolved_problems


@app.get("/user_info")
def user_info(db: Session = Depends(get_db)):
    get_user_info = db.query(User).all()
    return get_user_info
