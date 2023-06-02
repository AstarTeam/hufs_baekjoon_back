import time

import schedule

import unsolved_problem_project

from apscheduler.schedulers.background import BackgroundScheduler


# db 업데이트 하는 함수
def update_db():
    group_id = 405
    unsolved_problems = unsolved_problem_project.get_unsolved_by_group(group_id)
    print(unsolved_problems)
    print(len(unsolved_problems))
    unsolved_problem_project.update_user_rank(group_id)


# 08시 정각마다 업데이트 => 배포시 주석 해제
# scheduler = BackgroundScheduler()
# scheduler.add_job(update_db, 'cron', hour=8)
# scheduler.start()


# 5초마다 업데이트 하는 테스트용
# scheduler = BackgroundScheduler()
# scheduler.add_job(update_db, 'interval', seconds=5)
# scheduler.start()
