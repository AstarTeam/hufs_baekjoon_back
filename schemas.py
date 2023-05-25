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
class UserCreate(BaseModel):
    user_id: str
    user_name: str
    user_pw: str


# 데이터 명세 7 - PUT 마이페이지
class UserUpdateName(BaseModel):
    user_id: str
    user_name: str


# 데이터 명세 7 - PUT 마이페이지
class UserUpdatePw(BaseModel):
    user_id: str
    user_pw: str


# 데이터 명세 9 - GET 마이페이지(백준 인증) - 난수 생성 및 반환
class UserRand(BaseModel):
    user_id: str
    user_rand: str
