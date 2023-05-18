import json
from time import sleep
import requests
import sqlite3
from db_setting import db_setting

def check_user(user_id, is_checking_count):
    """
    특정 유저가 푼 문제 정보 받아오기
    :param str user_id: 유저 id
    :return int pages: 해당 유저가 푼 문제 페이지 수
    :return list items: 해당 유저가 푼 문제들에 대한 정보 list
    """
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    url = f"https://solved.ac/api/v3/search/problem?query=solved_by%3A{user_id}&sort=level&direction=desc"
    print(url)
    sleep(1)
    r_solved_by_user = requests.get(url)
    if r_solved_by_user.status_code == requests.codes.ok:
        solved_by_user = json.loads(r_solved_by_user.content.decode('utf-8'))
        count = solved_by_user.get("count")
        items = solved_by_user.get("items")
        pages = (count - 1) // 50 + 1

        # user 테이블에 user_id에 대한 항목 있는지 확인
        cur.execute("SELECT solved FROM user WHERE name = ?", (user_id,))
        user_solved = cur.fetchone()
        if user_solved is None:         # 없으면 새로운 행 (아이디, 푼 문제 수) 추가
            cur.execute("INSERT INTO user (name, solved) VALUES (?, ?)", (user_id, count))
        elif user_solved[0] == count:   # 문제 수 변경되지 않았으면 더이상 검색 X
            if not is_checking_count:   # 랭킹에 푼 문제 수 갱신하는 경우면 아래 실행 X
                pages = -1
        elif user_solved[0] != count:   # 문제 수 변경되었으면 solved 업데이트
            cur.execute("UPDATE user SET solved = ? WHERE name = ?", (count, user_id))
        conn.commit()
        cur.close()
        conn.close()
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
    입력된 group_id를 가진 그룹의 유저들이 푼 문제들의 번호에 대한 set를 반환
    :param group_id: 그룹 id
    :return set group_problems : group에서 푼 총 문제들의 번호 set
    """
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()
    # db의 problem 테이블에 저장 되어있는, 이미 푼 문제 번호 가져와서 사용
    cur.execute("SELECT * FROM problem") 
    problems = [row[0] for row in cur.fetchall()]

    group_users = get_user_in_group(group_id)
    group_problems = set()
    group_problems.update(problems)
    n = 1
    for user in group_users:
        print(n, " / ", len(group_users))
        n = n + 1
        pages, items = check_user(user, False)
        if pages == -1:     # check_user에서 count 변하지 않은 경우 생략
            continue
        get_solved_by_user = get_solved(user, pages, items)
        group_problems.update(get_solved_by_user)
    return group_problems

def get_problem_by_level(level):
    """
    입력된 level에 해당하는 문제들의 정보를 반환 (level은 unrated = 0 ~ ruby1 = 30으로 구분)
    :param int level:
    :return list problems: 해당 level 문제들의 정보(문제 번호, 제목) list
    """
    changed = True
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    url = f"https://solved.ac/api/v3/search/problem?query=tier%3A{level}"
    r_level_problem = requests.get(url)
    if r_level_problem.status_code == requests.codes.ok:
        level_problem = json.loads(r_level_problem.content.decode('utf-8'))
        count = level_problem.get("count")
        pages = (count - 1) // 50 + 1

        # level_problem 테이블에 level에 대한 항목 있는지 확인
        cur.execute("SELECT count FROM level_problem WHERE level = ?", (level,))
        row = cur.fetchone()

        if row is None:           # 없으면 새로운 행 (레벨, 해당 레벨 문제 수) 추가
            cur.execute("INSERT INTO level_problem (level, count) VALUES (?, ?)", (level, count))
            changed = True
        elif row[0] == count:     # 문제 수 변경되지 않았으면 더이상 검색 X  
            changed = False
        elif row[0] != count:     # 문제 수 변경되었으면 count 업데이트
            cur.execute("UPDATE level_problem SET count = ? WHERE level = ?", (count, level))
            changed = True
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("get_problem_by_level 요청 실패")

    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    if changed == False:    # 문제 수 변경되지 않았을 때는 db에 저장된 데이터 사용
        cur.execute("SELECT problem_data FROM level_problem WHERE level = ?", (level,))
        row = cur.fetchone()
        problems_str = row[0]
        problems = json.loads(problems_str)   
        conn.commit()
        cur.close()
        conn.close()
        return problems
    else:                   # 문제 수 변경되었을 때는 api 사용해서 가져오기
        problems = list()
        for page in range(1, pages + 1):
            page_url = f"{url}&page={page}"
            print(page_url)
            r_level_problem = requests.get(page_url)
            if r_level_problem.status_code == requests.codes.ok:
                level_problem = json.loads(r_level_problem.content.decode('utf-8'))
                items = level_problem.get("items")
                for item in items:
                    problem_data = (item.get("problemId"), item.get("titleKo"))
                    problems.append(problem_data)
            else:
                print("get_problem_by_level 요청 실패")

        problems_str = json.dumps(problems)
        cur.execute("UPDATE level_problem SET problem_data = ? WHERE level = ?", (problems_str, level))  
        conn.commit()
        cur.close()
        conn.close()
        return problems

def get_unsolved_by_group(group_id):
    """
    입력된 group_id의 그룹 유저들이 풀지 않은 문제들의 정보를 반환
    :param str group_id: 그룹 id
    :return list unsolved_problem: 해당 그룹 유저들이 풀지 못 한 문제들의 정보(문제 번호, 제목, 난이도) list
    """
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    # unsolved_problem 테이블 초기화
    cur.execute("DELETE FROM unsolved_problem")
    conn.commit()
    cur.close()
    conn.close()

    solved_problem = get_solved_by_group(group_id)
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    # 24시간 안에 풀린 문제 problem_24hr에 저장
    cur.execute("DELETE FROM problem_24hr")
    cur.execute("SELECT * FROM problem") 
    prev_problem = [row[0] for row in cur.fetchall()]
    solved_in_24hr = get_solved_in_24hr(prev_problem, solved_problem)

    for problem in solved_in_24hr:
        cur.execute("INSERT OR IGNORE INTO problem_24hr(id) VALUES(?)", (problem,))

    # 그룹이 푼 문제를 problem 테이블에 저장
    for problem in solved_problem:
        cur.execute("INSERT OR IGNORE INTO problem(id) VALUES(?)", (problem,))
    conn.commit()
    cur.close()
    conn.close()

    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()
    unsolved_problem = list()
    for level in range(1, 31):
        level_problem = get_problem_by_level(level)
        unsolved_level_problem = [(x[0], x[1], level) for x in level_problem if x[0] not in solved_problem]
        if len(unsolved_level_problem) == 0:
            print(f"{level} 레벨의 문제는 전부 풀었습니다.")
        else:
            unsolved_problem.extend(unsolved_level_problem)

    for problem in unsolved_problem:
        cur.execute("INSERT INTO unsolved_problem (problem_num, problem_title, problem_lev, problem_link) VALUES (?, ?, ?, ?)", 
                    (problem[0], problem[1], problem[2], f"https://www.acmicpc.net/problem/{problem[0]}"))
    conn.commit()
    cur.close()
    conn.close()

    # 랭킹에 쓰이는 그룹 내 유저가 푼 누적 문제 수 DB에 저장
    group_users = get_user_in_group(group_id)
    for user in group_users:
        pages, items = check_user(user, True)
        get_solved_by_user = get_solved(user, pages, items)
        get_users_solved_count_in_24hr(user, solved_in_24hr, get_solved_by_user)
    return unsolved_problem

def get_solved_in_24hr(prev_problem, current_problem):
    """
    24시간 안에 풀린 문제들 반환
    :param set prev_problem: 24시간 전까지 풀린 문제들
    :param set current_problem: 현재까지 풀린 문제들
    :return list solved_in_24hr: 24시간 안에 풀린 문제들의 list
    """
    solved_in_24hr = list()
    solved_in_24hr = [x for x in current_problem if x not in prev_problem]
    return solved_in_24hr

def get_users_solved_count_in_24hr(user, group_solved_problem, user_solved_problem):
    """
    24시간 안에 푼 문제들 중 해당 유저가 푼 문제 수 DB에 누적하여 저장
    :param list group_solved_problem: 24시간 안에 그룹에서 풀린 문제들
    :param list user_solved_problem: 해당 유저가 푼 모든 문제들
    """
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    cur.execute("INSERT OR IGNORE INTO user_solved_count(id) VALUES(?)", (user,))
    cur.execute("SELECT count FROM user_solved_count WHERE id = ?", (user,))
    row = cur.fetchone()
    prev_solved_count = row[0]
    conn.commit()
    cur.close()
    conn.close()   

    user_solved_in_24hr = list()
    user_solved_in_24hr = [x for x in user_solved_problem if x in group_solved_problem]
    total_count = prev_solved_count + len(user_solved_in_24hr)

    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()
    cur.execute("UPDATE user_solved_count SET count = ? WHERE id = ?", (total_count, user))
    conn.commit()
    cur.close()
    conn.close()   
    return

group_id = 600 #405
db_setting(group_id)
unsolved_problems = get_unsolved_by_group(group_id)
print(unsolved_problems)
print(len(unsolved_problems))
