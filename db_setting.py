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
    # 그룹에서 안 푼 모든 문제 정보(문제 번호, 제목, 난이도, 링크, 도전자 수) 저장
    cur.execute('CREATE TABLE IF NOT EXISTS unsolved_problem(problem_num int PRIMARY KEY, problem_title text, problem_lev int, problem_link text, problem_challengers int)')
    # 그룹에서 24시간 안에 푼 문제 번호 저장
    cur.execute('CREATE TABLE IF NOT EXISTS problem_24hr(id int PRIMARY KEY)')

    # 랭킹 관련 테이블
    cur.execute('''CREATE TABLE IF NOT EXISTS rank(hufs_rank int PRIMARY KEY, hufs_now_solved int not null, hufs_pre_solved int, 
    high_rank_name text not null, high_rank_now_solved int not null, high_rank_pre_solved int,
    low_rank_name text not null, low_rank_now_solved int not null, low_rank_pre_solved int)''')

    conn.commit()
    cur.close()
    conn.close()
