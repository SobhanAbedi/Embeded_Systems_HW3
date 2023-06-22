#!/usr/bin/env python
"""
main.py - parser for task set from JSON file
"""

import json
import sys

from job import Job, EMPTY_JOB
from task import Task, EMPTY_TASK
from task import TaskSetJsonKeys as TSJK
from taskSet import TaskSet, EventType
from semaphore import SemaphoreSet, SemaphoreAP


def main() -> None:
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "taskset1.json"

    with open(file_path) as json_data:
        data = json.load(json_data)

    task_set = TaskSet(data)
    task_set.print_tasks()
    task_set.print_jobs()
    task_set.print_events()

    resources = task_set.get_all_resources()
    event_list = task_set.get_event_list()
    curr_event = 0
    events: dict[float, list[tuple[EventType, Job]]] = task_set.get_events()
    ready_queue: list[Job] = []
    waiting_queue: list[Job] = []
    highest_priorities = task_set.get_highest_priorities()
    semaphores = SemaphoreSet(resources, access_protocol=SemaphoreAP.HLP, resources_highest_priority=highest_priorities)
    schedule: list[tuple[float, float, Job, int]] = []

    event_count = len(event_list)
    for i in range(event_count - 1):
        event_time = event_list[i]
        # print(f'Current Time: {event_time}')
        next_event_time = event_list[i + 1]
        for event in events[event_time]:
            if event[0] == EventType.RELEASE:
                event[1].release(semaphores, ready_queue, waiting_queue)
            elif event[0] == EventType.DEADLINE:
                event[1].end()

        curr_time = event_time

        while curr_time < next_event_time:
            # print(f'Ready Queue Length is {len(ready_queue)} @ t = {curr_time}')
            if len(ready_queue) == 0:
                schedule.append((curr_time, next_event_time, EMPTY_JOB, 0))
                curr_time = next_event_time
            else:
                selected_job = ready_queue[0]
                progression, resource = selected_job.execute(next_event_time - curr_time)
                if progression == 0:
                    print("BLOCKED!")
                if progression > 0:
                    edited = False
                    if len(schedule) > 0:
                        progress = schedule[-1]
                        if progress[3] == resource and progress[2] == selected_job and progress[1] == curr_time:
                            schedule[-1] = (progress[0], curr_time + progression, selected_job, resource)
                            edited = True
                    if not edited:
                        schedule.append((curr_time, curr_time + progression, selected_job, resource))
                curr_time += progression

    print("\nSchedule:")
    for progress in schedule:
        if progress[2] != EMPTY_JOB:
            if progress[3] > 0:
                print(f'{progress[0]}->{progress[1]}: {progress[2].short_form()} using resource {progress[3]}')
            else:
                print(f'{progress[0]}->{progress[1]}: {progress[2].short_form()}')
        else:
            print(f'{progress[0]}->{progress[1]}: Free')


if __name__ == "__main__":
    main()
