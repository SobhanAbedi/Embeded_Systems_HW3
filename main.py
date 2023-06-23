#!/usr/bin/env python
"""
main.py - parser for task set from JSON file
"""

import json
import sys
import plotly.express as px
import pandas as pd

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
    semaphores = SemaphoreSet(resources, access_protocol=SemaphoreAP.PIP, resources_highest_priority=highest_priorities)
    schedule = pd.DataFrame([])

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
                # schedule.append((curr_time, next_event_time, EMPTY_JOB, 0))
                curr_time = next_event_time
            else:
                selected_job = ready_queue[0]
                progression, resource = selected_job.execute(next_event_time - curr_time)
                # if progression == 0:
                #     print("BLOCKED!")
                if progression > 0:
                    edited = False
                    if not schedule.empty:
                        progress = schedule.loc[schedule.index[-1]]
                        if (progress.at['Resource'] == str(resource) and progress['Task'] == selected_job.task.id and
                                progress['Job'] == selected_job.id and progress['End'] == curr_time):
                            schedule.at[schedule.index[-1], 'End'] = curr_time + progression
                            edited = True
                    if not edited:
                        task_id = 0
                        job_id = 0
                        if selected_job.task != EMPTY_JOB:
                            task_id = selected_job.task.id
                            job_id = selected_job.id
                        new_row = pd.DataFrame([
                            dict(Start=curr_time, End=curr_time + progression, Task=task_id, Job=job_id,
                                 Resource=str(resource))
                        ])
                        schedule = pd.concat([schedule, new_row], ignore_index=True)
                curr_time += progression

    print("\nSchedule:")
    print(schedule)

    for task in task_set:
        for resource in resources:
            range_set_row = pd.DataFrame([
                dict(Start=0, End=0, Task=task.id, Job=0, Resource=str(resource))
            ])
            schedule = pd.concat([schedule, range_set_row], ignore_index=True)

    schedule['Time'] = schedule['End'] - schedule['Start']
    fig = px.bar(schedule, base="Start", x="Time", y="Task", color="Resource", orientation='h')
    fig.update_yaxes(autorange="reversed")
    fig.show()


if __name__ == "__main__":
    main()
