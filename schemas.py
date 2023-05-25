from pydantic import BaseModel


class ProblemBase(BaseModel):
    id: int
    title: str
    tier: int


class UnsolvedProblem(BaseModel):
    id: int
    title: str
    tier: int


class User(BaseModel):
    user_id: str
    user_pw: str
    user_name: str
    solved_count: int
    user_baekjoon_id: str


class UserCreate(BaseModel):
    user_id: str
    user_name: str
    user_pw: str
