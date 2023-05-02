from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from pydantic import BaseModel
from database import SessionLocal, get_db
from models import Unsolved_Problem
from unsolved_problem_project import get_unsolved_by_group

app = FastAPI()

@app.post("/unsolved_by_group/{group_id}")
async def save_unsolved_problems(group_id: str, db: Session = Depends(get_db)):
    unsolved_problems = get_unsolved_by_group(group_id)
    for problem_num, problem_lev in unsolved_problems.items():
        unsolved_problem = Unsolved_Problem(problem_num=problem_num, problem_lev=problem_lev)
        db.add(unsolved_problem)
    db.commit()
    return {"message": "Unsolved problems saved successfully"}


