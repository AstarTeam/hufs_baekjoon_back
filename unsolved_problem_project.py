import json
from time import sleep
import requests
import sqlite3
import os
import shutil
from db_setting import db_setting

is_interrupted = False

def check_user(user_id, is_checking_count):
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

        cur.execute("SELECT solved_count FROM baekjoon_user WHERE id = ?", (user_id,))
        user_solved = cur.fetchone()
        if user_solved is None:        
            cur.execute("INSERT INTO baekjoon_user (id, solved_count) VALUES (?, ?)", (user_id, count))
        elif user_solved[0] == count:   
                pages = -1
        elif user_solved[0] != count:   
            cur.execute("UPDATE baekjoon_user SET solved_count = ? WHERE id = ?", (count, user_id))
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("check_user 요청 실패")
        print(r_solved_by_user.status_code)
        is_interrupted = True
    return pages, items

def get_solved(user_id, pages, items):
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
            is_interrupted = True

    problems_str = json.dumps(solved_problems)
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()
    cur.execute("UPDATE baekjoon_user SET solved_list = ? WHERE id = ?", (problems_str, user_id))
    conn.commit()
    cur.close()
    conn.close()
    return solved_problems

def get_user_in_group(group_id):
    url = f"https://solved.ac/api/v3/ranking/in_organization?organizationId={group_id}"
    r_user_in_group = requests.get(url)
    if r_user_in_group.status_code == requests.codes.ok:
        user_in_group = json.loads(r_user_in_group.content.decode('utf-8'))
        pages = (user_in_group.get("count") - 1) // 50 + 1
    else:
        print("get_user_in_group 요청 실패")
        is_interrupted = True

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
            is_interrupted = True
    return users

def get_solved_by_group(group_id):
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()
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
        if pages == -1:  
            continue
        get_solved_by_user = get_solved(user, pages, items)
        group_problems.update(get_solved_by_user)
    return group_problems

def get_problem_by_level(level):
    changed = True
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    url = f"https://solved.ac/api/v3/search/problem?query=tier%3A{level}"
    r_level_problem = requests.get(url)
    if r_level_problem.status_code == requests.codes.ok:
        level_problem = json.loads(r_level_problem.content.decode('utf-8'))
        count = level_problem.get("count")
        pages = (count - 1) // 50 + 1

        cur.execute("SELECT count FROM level_problem WHERE level = ?", (level,))
        row = cur.fetchone()

        if row is None:          
            cur.execute("INSERT INTO level_problem (level, count) VALUES (?, ?)", (level, count))
            changed = True
        elif row[0] == count:    
            cur.execute("UPDATE level_problem SET count = ? WHERE level = ?", (count, level))
            changed = True
        conn.commit()
        cur.close()
        conn.close()
    else:
        print("get_problem_by_level 요청 실패")
        is_interrupted = True

    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    if changed == False:   
        cur.execute("SELECT problem_data FROM level_problem WHERE level = ?", (level,))
        row = cur.fetchone()
        problems_str = row[0]
        problems = json.loads(problems_str)   
        conn.commit()
        cur.close()
        conn.close()
        return problems
    else:               
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
                is_interrupted = True

        problems_str = json.dumps(problems)
        cur.execute("UPDATE level_problem SET problem_data = ? WHERE level = ?", (problems_str, level))  
        conn.commit()
        cur.close()
        conn.close()
        return problems

def get_unsolved_by_group(group_id):
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    cur.execute("DELETE FROM unsolved_problem")
    conn.commit()
    cur.close()
    conn.close()

    solved_problem = get_solved_by_group(group_id)
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    cur.execute("DELETE FROM problem_24hr")
    cur.execute("SELECT * FROM problem") 
    prev_problem = [row[0] for row in cur.fetchall()]
    solved_in_24hr = get_solved_in_24hr(prev_problem, solved_problem)

    for problem in solved_in_24hr:
        cur.execute("INSERT OR IGNORE INTO problem_24hr(id) VALUES(?)", (problem,))

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
        cur.execute("INSERT or REPLACE INTO unsolved_problem (problem_num, problem_title, problem_lev, problem_link) VALUES (?, ?, ?, ?)", 
                    (problem[0], problem[1], problem[2], f"https://www.acmicpc.net/problem/{problem[0]}"))
    conn.commit()
    cur.close()
    conn.close()

    group_users = get_user_in_group(group_id)
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()
    for user in group_users:
        cur.execute("SELECT solved_list FROM baekjoon_user WHERE id = ?", (user,))
        row = cur.fetchone()
        solved_list_str = row[0]
        solved_list = json.loads(solved_list_str)   
        get_users_solved_count_in_24hr(user, solved_in_24hr, solved_list)
    return unsolved_problem

def get_solved_in_24hr(prev_problem, current_problem):
    solved_in_24hr = list()
    solved_in_24hr = [x for x in current_problem if x not in prev_problem]
    return solved_in_24hr

def get_users_solved_count_in_24hr(user, group_solved_problem, user_solved_problem):
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    cur.execute("SELECT accume_count FROM baekjoon_user WHERE id = ?", (user,))
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
    cur.execute("UPDATE baekjoon_user SET accume_count = ? WHERE id = ?", (total_count, user))
    conn.commit()
    cur.close()
    conn.close()   
    return

def update_user_rank(group_id):
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM user")
    cur.execute("SELECT user_baekjoon_id, RANK() OVER(ORDER BY user_solved_count DESC) rank FROM user where user_auth==1")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("UPDATE user SET user_rank = ? WHERE user_baekjoon_id = ?", (row[1], row[0]))
        conn.commit()
                    
    cur.close()
    conn.close()   
    return

def copy_db(group_id):
    origin_file_path = os.path.join(os.getcwd(), str(group_id)+'_unsolved.db')
    copy_file_path = os.path.join(os.getcwd(), str(group_id)+'_copy_unsolved.db')
    shutil.copy(origin_file_path, copy_file_path)
    
group_id = 405 #600
db_setting(group_id) 
copy_db(group_id)
unsolved_problems = get_unsolved_by_group(group_id)
print(unsolved_problems)
print(len(unsolved_problems))
update_user_rank(group_id)

if is_interrupted:
    os.remove(os.path.join(os.getcwd(), str(group_id)+'_unsolved.db'))
    os.rename(os.path.join(os.getcwd(),str(group_id)+'_copy_unsolved.db'), str(group_id)+'_unsolved.db')
else:
    os.remove(os.path.join(os.getcwd(), str(group_id)+'_copy_unsolved.db'))
