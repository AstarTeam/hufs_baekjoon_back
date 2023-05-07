import schedule
import time
from unsolved_problem_project import get_unsolved_by_group

schedule.every().day.at("05:30").do(get_unsolved_by_group)

while True:
    schedule.run_pending()
    time.sleep(1)