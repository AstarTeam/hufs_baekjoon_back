from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    user_pw: str
    user_name: str
    solved_count: int
    user_baekjoon_id: str


# 데이터 명세 5 - 회원가입
class UserCreate(BaseModel):
    user_id: str
    user_name: str
    user_pw: str


# 데이터 명세 6 - POST 로그인
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    user_auth: int
