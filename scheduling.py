import time

import schedule

import unsolved_problem_project

from apscheduler.schedulers.background import BackgroundScheduler


def update_db():
    group_id = 405
    unsolved_problems = unsolved_problem_project.get_unsolved_by_group(group_id)
    print(unsolved_problems)
    print(len(unsolved_problems))
    unsolved_problem_project.update_user_rank(group_id)


scheduler = BackgroundScheduler()
scheduler.add_job(update_db, 'cron', hour=8)
scheduler.start()
