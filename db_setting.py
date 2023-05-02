import sqlite3

def db_setting(group_id):
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    # 유저 별 이름, 푼 문제 수 저장
    cur.execute('CREATE TABLE IF NOT EXISTS user(name text PRIMARY KEY, solved int)')
    # 그룹에서 푼 모든 문제 번호 저장
    cur.execute('CREATE TABLE IF NOT EXISTS problem(id int PRIMARY KEY)')
    # 각 레벨 별 문제 수, 문제 정보(문제 번호, 제목) 저장
    cur.execute('CREATE TABLE IF NOT EXISTS level_problem(level int PRIMARY KEY, count int, problem_data TEXT)')

    conn.commit()
    cur.close()
    conn.close()