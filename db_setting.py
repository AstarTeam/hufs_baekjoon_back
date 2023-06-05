import sqlite3


def db_setting(group_id):
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()

    # 백준 사이트의 그룹 내 모든 유저 id, 푼 문제 수, 우리 사이트에서 사용하는 누적 개수 저장
    cur.execute('''CREATE TABLE IF NOT EXISTS baekjoon_user(
                id text PRIMARY KEY,
                solved int,
                accume_count int default 0)''')

    # 유저 닉네임, 푼 문제 수 이후 회원가입 시 정보 저장
    cur.execute('''CREATE TABLE IF NOT EXISTS user(
                user_id text PRIMARY KEY, 
                user_pw text, 
                user_name text, 
                user_solved_count int default 0, 
                user_baekjoon_id text, 
                user_rank int)''')
    
    # 그룹에서 푼 모든 문제 번호 저장
    cur.execute('CREATE TABLE IF NOT EXISTS problem(id int PRIMARY KEY)')
    
    # 각 레벨 별 문제 수, 문제 정보(문제 번호, 제목) 저장
    cur.execute('CREATE TABLE IF NOT EXISTS level_problem(level int PRIMARY KEY, count int, problem_data text)')
    
    # 그룹에서 안 푼 모든 문제 정보(문제 번호, 제목, 난이도, 링크, 도전자 수) 저장
    cur.execute('''CREATE TABLE IF NOT EXISTS unsolved_problem(
                problem_num int PRIMARY KEY, 
                problem_title text, 
                problem_lev int, 
                problem_link text, 
                problem_challengers int default 0)''')
    
    # 그룹에서 24시간 안에 푼 문제 번호 저장
    cur.execute('CREATE TABLE IF NOT EXISTS problem_24hr(id int PRIMARY KEY)')

    # 도전자 테이블 작성
    cur.execute('''CREATE TABLE IF NOT EXISTS challengers(
                id int PRIMARY KEY,
                challenger_id text,
                challenge_problem int,
                FOREIGN KEY (challenger_id) REFERENCES user(user_id),
                FOREIGN KEY (challenge_problem) REFERENCES unsolved_problem(problem_num))''')

    # 랭킹 관련 테이블
    cur.execute('''CREATE TABLE IF NOT EXISTS rank(
                hufs_rank int PRIMARY KEY, 
                hufs_now_solved int not null, 
                hufs_pre_solved int, 
                high_rank_name text not null, 
                high_rank_now_solved int not null, 
                high_rank_pre_solved int,
                low_rank_name text not null, 
                low_rank_now_solved int not null, 
                low_rank_pre_solved int)''')
    # 추천 문제 테이블
    cur.execute('''CREATE TABLE IF NOT EXISTS recommend(
                id int PRIMARY KEY,
                problem_num int not null,
                problem_title text not null,
                problem_lev int not null,
                problem_link text not null)''')

    conn.commit()
    cur.close()
    conn.close()
