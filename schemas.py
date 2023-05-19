from pydantic import BaseModel, validator   # validator  추가


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


# 데이터 명세 5 - 회원가입(작성중)
class UserCreate(User):
    user_rand: str
    user_img: bytes = None


# 데이터 명세 7 - PUT 마이페이지
class UserUpdateName(BaseModel):
    user_id: str
    user_name: str


# 데이터 명세 7 - PUT 마이페이지
class UserUpdatePw(BaseModel):
    user_id: str
    user_pw: str