import json
from time import sleep
import requests
from sqlalchemy.testing import db

from models import Unsolved_Problem
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, get_db
import sqlite3
"from db_setting import db_setting"

def check_user(user_id):
    """
    특정 유저가 푼 문제 정보 받아오기
    :param str user_id: 유저 id
    :return int pages: 해당 유저가 푼 문제 페이지 수
    :return list items: 해당 유저가 푼 문제들에 대한 정보 list
    """
    url = f"https://solved.ac/api/v3/search/problem?query=solved_by%3A{user_id}&sort=level&direction=desc"
    print(url)
    sleep(1)
    r_solved_by_user = requests.get(url)
    if r_solved_by_user.status_code == requests.codes.ok:
        solved_by_user = json.loads(r_solved_by_user.content.decode('utf-8'))
        count = solved_by_user.get("count")
        items = solved_by_user.get("items")
        pages = (count - 1) // 50 + 1
    else:
        print("check_user 요청 실패")
        print(r_solved_by_user.status_code)
    return pages, items

def get_solved(user_id, pages, items):
    """
    user_id와 check_user를 통해 받아온 pages와 items를 통해 해당 user가 푼 문제들의 번호를 (level의 내림차순) list로 반환
    :param str user_id: 유저 id
    :param int pages: 해당 유저가 푼 문제 페이지 수
    :param list items: 해당 유저가 푼 문제들에 대한 정보 배열
    :return list solved_problems: 해당 유저가 푼 문제들의 번호 list
    """
    url = f"https://solved.ac/api/v3/search/problem?query=s%40{user_id}&sort=level&direction=desc"
    solved_problems = []
    for item in items:
        solved_problems.append(item.get("problemId"))
    for page in range(1, pages + 1):
        sleep(1)
        page_url = f"{url}&page={page}"
        print(page_url)
        r_solved_in_page = requests.get(page_url)
        if r_solved_in_page.status_code == requests.codes.ok:
            solved_in_page = json.loads(r_solved_in_page.content.decode('utf-8'))
            items = solved_in_page.get("items")
            for item in items:
                solved_problems.append(item.get("problemId"))
        else:
            print("get_solved 요청 실패")
            print(r_solved_in_page.status_code)
            print(url)
    return solved_problems

def get_user_in_group(group_id):
    """"
    :param str group_id: 그룹 id
    :return list userList: 그룹에 속한 총 user들의 list
    """
    url = f"https://solved.ac/api/v3/ranking/in_organization?organizationId={group_id}"
    r_user_in_group = requests.get(url)
    if r_user_in_group.status_code == requests.codes.ok:
        user_in_group = json.loads(r_user_in_group.content.decode('utf-8'))
        pages = (user_in_group.get("count") - 1) // 50 + 1
    else:
        print("get_user_in_group 요청 실패")

    users = []
    for page in range(1, pages + 1):
        page_url = f"{url}&page={page}"
        print(page_url)
        r_user_in_group = requests.get(page_url)
        if r_user_in_group.status_code == requests.codes.ok:
            user_in_group = json.loads(r_user_in_group.content.decode('utf-8'))
            items = user_in_group.get("items")
            for item in items:
                users.append(item.get("handle"))
        else:
            print("get_user_in_group 요청 실패")
    return users

def get_solved_by_group(group_id):
    """
    입력된 group_id를 가진 그룹의 유저들이 푼 문제들의 번호 list를 반환
    :param group_id: 그룹 id
    :return set group_problems : group에서 푼 총 문제들의 번호 list
    """
    group_users = get_user_in_group(group_id)
    group_problems = set()
    n = 1
    for user in group_users:
        print(n, " / ", len(group_users))
        n = n + 1
        pages, items = check_user(user)
        if pages == -1:
            continue
        get_solved_by_user = get_solved(user, pages, items)
        print(get_solved_by_user)
        group_problems.update(get_solved_by_user)
    return group_problems

def get_problem_by_level(level):
    """
    입력된 level에 해당하는 문제들을 반환 (level은 unrated = 0 ~ ruby1 = 30으로 구분)
    :param int level:
    :return set problems: 해당 level 문제들의 set
    """
    url = f"https://solved.ac/api/v3/search/problem?query=tier%3A{level}"
    r_level_problem = requests.get(url)
    if r_level_problem.status_code == requests.codes.ok:
        level_problem = json.loads(r_level_problem.content.decode('utf-8'))
        pages = (level_problem.get("count") - 1) // 50 + 1
    else:
        print("get_problem_by_level 요청 실패")

    problems = set()
    for page in range(1, pages + 1):
        page_url = f"{url}&page={page}"
        print(page_url)
        r_level_problem = requests.get(page_url)
        if r_level_problem.status_code == requests.codes.ok:
            level_problem = json.loads(r_level_problem.content.decode('utf-8'))
            items = level_problem.get("items")
            for item in items:
                problems.add(item.get("problemId"))
        else:
            print("get_problem_by_level 요청 실패")
    return problems

def get_unsolved_by_group(group_id, db:Session):
    """
    입력된 group_id의 그룹 유저들이 풀지 않은 문제들을 level별로 반환
    :param str group_id: 그룹 id
    :return dict unsolved_level_problem: 해당 그룹 유저들이 풀지 못 한 문제들의 set
    """
    solved_problem = get_solved_by_group(group_id)
    unsolved_problem = dict()
    for level in range(1, 31):
        level_problem = get_problem_by_level(level)
        unsolved_level_problem = {(x, level) for x in level_problem if x not in solved_problem}
        if len(unsolved_level_problem) == 0:
            print(f"{level} 레벨의 문제는 전부 풀었습니다.")
        else:
            unsolved_problem.update(unsolved_level_problem)
    for problem_num, problem_lev in unsolved_problem.items():
        unsolved_problem = Unsolved_Problem(problem_num=problem_num, problem_lev=problem_lev)
        db.add(unsolved_problem)
    db.commit()
    return unsolved_problem

def get_solved_in_24hr(prev_problem, current_problem):
    """
    24시간 안에 풀린 문제들 반환
    :param set prev_problem: 24시간 전까지 풀린 문제들
    :param set current_problem: 현재까지 풀린 문제들
    :return set solved_in_24hr: 24시간 안에 풀린 문제들의 set
    """
    solved_in_24hr = set()
    solved_in_24hr = [x for x in current_problem if x not in prev_problem]
    return solved_in_24hr

user_id = "rbals980"
group_id = 600

"""
pages, items = check_user(user_id)
solved_problems = get_solved(user_id, pages, items)
print(solved_problems)
print(f"푼 문제수 : {len(solved_problems)}")

users = get_user_in_group(405)
print(users)
print(len(users))

solved_in_group = get_solved_by_group(group_id)
print(solved_in_group)
"""

# unsolved_problems = get_unsolved_by_group(group_id)
# print(unsolved_problems)
# print(len(unsolved_problems))
if __name__ == "__main__":
    group_id = 600
    db = SessionLocal()
    unsolved_problems = get_unsolved_by_group(group_id, db)
    db.close()