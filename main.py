#!/usr/bin/env python
"""
main.py - parser for task set from JSON file
"""

import json
import sys

from job import Job, EMPTY_JOB
from task import Task, EMPTY_TASK
from taskSet import TaskSet
from semaphore import Semaphore


def main() -> None:
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "taskset.json"

    with open(file_path) as json_data:
        task_set_data = json.load(json_data)

    task_set = TaskSet(task_set_data)
    task_set.print_tasks()
    task_set.print_jobs()

    task1 = task_set.get_task_by_id(1)
    task2 = task_set.get_task_by_id(2)

    print("Resource list of task 1")
    print(task1.get_all_resources())
    print("Resource list of task 2")
    print(task2.get_all_resources())
    print("Resource list of entire TaskSet")
    print(task_set.get_all_resources())

    jobs = task1.get_jobs() + task2.get_jobs()
    print("\nAll Jobs:")
    for job in jobs:
        print(job)

    jobs.sort()

    print("\nAll Jobs Sorted:")
    for job in jobs:
        print(job)

    semaphore = Semaphore(1)
    if semaphore.taken:
        print("Semaphore is Taken")
    else:
        print("Semaphore is Free")

    semaphore.wait(jobs[1])
    print("Added Job 1")
    print("Priority is " + str(semaphore.get_priority()))

    if semaphore.taken:
        print("Semaphore is Taken")
    else:
        print("Semaphore is Free")

    semaphore.wait(jobs[0])
    print("Added Job 0")
    print("Priority is " + str(semaphore.get_priority()))

    if semaphore.taken:
        print("Semaphore is Taken")
    else:
        print("Semaphore is Free")

    semaphore.signal(jobs[0])
    print("Removed Job 0")
    print("Priority is " + str(semaphore.get_priority()))

    if semaphore.taken:
        print("Semaphore is Taken")
    else:
        print("Semaphore is Free")

    semaphore.signal(jobs[1])
    print("Removed Job 1")
    print("Priority is " + str(semaphore.get_priority()))

    if semaphore.taken:
        print("Semaphore is Taken")
    else:
        print("Semaphore is Free")


if __name__ == "__main__":
    main()
