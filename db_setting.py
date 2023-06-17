import sqlite3

def db_setting(group_id):
    conn = sqlite3.connect(str(group_id)+'_unsolved.db')
    cur = conn.cursor()


    cur.execute('''CREATE TABLE IF NOT EXISTS baekjoon_user(
                id text PRIMARY KEY,
                solved_count int,
                solved_list text,
                accume_count int default 0)''')


    cur.execute('''CREATE TABLE IF NOT EXISTS user(
                user_id text PRIMARY KEY, 
                user_pw text, 
                user_name text, 
                user_solved_count int default 0, 
                user_baekjoon_id text,
                user_rank int, 
                user_auth int,
                user_rand int)''')

    cur.execute('CREATE TABLE IF NOT EXISTS problem(id int PRIMARY KEY)')

    cur.execute('CREATE TABLE IF NOT EXISTS level_problem(level int PRIMARY KEY, count int, problem_data text)')

    cur.execute('''CREATE TABLE IF NOT EXISTS unsolved_problem(
                problem_num int PRIMARY KEY, 
                problem_title text, 
                problem_lev int, 
                problem_link text, 
                problem_challengers int default 0)''')

    cur.execute('CREATE TABLE IF NOT EXISTS problem_24hr(id int PRIMARY KEY)')

    cur.execute('''CREATE TABLE IF NOT EXISTS challengers(
                id int PRIMARY KEY,
                challenger_id text,
                challenge_problem int,
                FOREIGN KEY (challenger_id) REFERENCES user(user_id),
                FOREIGN KEY (challenge_problem) REFERENCES unsolved_problem(problem_num))''')

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

    cur.execute('''CREATE TABLE IF NOT EXISTS recommend(
                id int PRIMARY KEY,
                problem_num int not null,
                problem_title text not null,
                problem_lev int not null,
                problem_link text not null)''')

    conn.commit()
    cur.close()
    conn.close()
