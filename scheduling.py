import schedule
import time
import unsolved_problem_project

# db 업데이트 하는 함수
def update_db():
    group_id = 405
    unsolved_problems = unsolved_problem_project.get_unsolved_by_group(group_id)
    print(unsolved_problems)
    print(len(unsolved_problems))
    unsolved_problem_project.update_user_rank(group_id)

# 매일 08:00마다 update_db 함수 작동
schedule.every(24).day.at("08:00").do(update_db)

# 무한 루프 돌면서 스케줄 유지
while True:
    schedule.run_pending()
    time.sleep(1)