#!/usr/bin/env python

"""
main.py - parser for task set from JSON file
"""

import json
import sys


class TaskSetJsonKeys(object):
    # Task set
    KEY_TASKSET = "taskset"

    # Task
    KEY_TASK_ID = "taskId"
    KEY_TASK_PERIOD = "period"
    KEY_TASK_WCET = "wcet"
    KEY_TASK_DEADLINE = "deadline"
    KEY_TASK_OFFSET = "offset"
    KEY_TASK_SECTIONS = "sections"

    # Schedule
    KEY_SCHEDULE_START = "startTime"
    KEY_SCHEDULE_END = "endTime"

    # Release times
    KEY_RELEASETIMES = "releaseTimes"
    KEY_RELEASETIMES_JOBRELEASE = "timeInstant"
    KEY_RELEASETIMES_TASKID = "taskId"


class TaskSetIterator:
    def __init__(self, task_set):
        self.taskSet = task_set
        self.index = 0
        self.keys = iter(task_set.tasks)

    def __next__(self):
        key = next(self.keys)
        return self.taskSet.tasks[key]


class TaskSet(object):
    def __init__(self, task_set_data):
        self.parse_data_to_tasks(task_set_data)
        self.build_job_releases(task_set_data)
        self.jobs = []
        self.tasks = {}

    def parse_data_to_tasks(self, task_set_data):
        task_set = {}

        for taskData in task_set_data[TaskSetJsonKeys.KEY_TASKSET]:
            task = Task(taskData)

            if task.id in task_set:
                print("Error: duplicate task ID: {0}".format(task.id))
                return

            if task.period < 0 and task.relativeDeadline < 0:
                print("Error: aperiodic task must have positive relative deadline")
                return

            task_set[task.id] = task

        self.tasks = task_set

    def build_job_releases(self, task_set_data):
        jobs = []

        if TaskSetJsonKeys.KEY_RELEASETIMES in task_set_data:  # necessary for sporadic releases
            for job_release in task_set_data[TaskSetJsonKeys.KEY_RELEASETIMES]:
                release_time = float(job_release[TaskSetJsonKeys.KEY_RELEASETIMES_JOBRELEASE])
                task_id = int(job_release[TaskSetJsonKeys.KEY_RELEASETIMES_TASKID])

                job = self.get_task_by_id(task_id).spawn_job(release_time)
                jobs.append(job)
        else:
            schedule_start_time = float(task_set_data[TaskSetJsonKeys.KEY_SCHEDULE_START])
            schedule_end_time = float(task_set_data[TaskSetJsonKeys.KEY_SCHEDULE_END])
            for task in self:
                t = max(task.offset, schedule_start_time)
                while t < schedule_end_time:
                    job = task.spawn_job(t)
                    if job is not None:
                        jobs.append(job)

                    if task.period >= 0:
                        t += task.period  # periodic
                    else:
                        t = schedule_end_time  # aperiodic

        self.jobs = jobs

    def __contains__(self, elt):
        return elt in self.tasks

    def __iter__(self):
        return TaskSetIterator(self)

    def __len__(self):
        return len(self.tasks)

    def get_task_by_id(self, task_id):
        return self.tasks[task_id]

    def print_tasks(self):
        print("\nTask Set:")
        for task in self:
            print(task)

    def print_jobs(self):
        print("\nJobs:")
        for task in self:
            for job in task.get_jobs():
                print(job)


class Task(object):
    def __init__(self, task_dict):
        self.id = int(task_dict[TaskSetJsonKeys.KEY_TASK_ID])
        self.period = float(task_dict[TaskSetJsonKeys.KEY_TASK_PERIOD])
        self.wcet = float(task_dict[TaskSetJsonKeys.KEY_TASK_WCET])
        self.relativeDeadline = float(
            task_dict.get(TaskSetJsonKeys.KEY_TASK_DEADLINE, task_dict[TaskSetJsonKeys.KEY_TASK_PERIOD]))
        self.offset = float(task_dict.get(TaskSetJsonKeys.KEY_TASK_OFFSET, 0.0))
        self.sections = task_dict[TaskSetJsonKeys.KEY_TASK_SECTIONS]

        self.lastJobId = 0
        self.lastReleasedTime = 0.0

        self.jobs = []

    def get_all_resources(self):
        # TODO
        return

    def spawn_job(self, release_time):
        if self.lastReleasedTime > 0 and release_time < self.lastReleasedTime:
            print("INVALID: release time of job is not monotonic")
            return None

        if self.lastReleasedTime > 0 and release_time < self.lastReleasedTime + self.period:
            print("INVDALID: release times are not separated by period")
            return None

        self.lastJobId += 1
        self.lastReleasedTime = release_time

        job = Job(self, self.lastJobId, release_time)

        self.jobs.append(job)
        return job

    def get_jobs(self):
        return self.jobs

    def get_job_by_id(self, job_id):
        if job_id > self.lastJobId:
            return None

        job = self.jobs[job_id - 1]
        if job.id == job_id:
            return job

        for job in self.jobs:
            if job.id == job_id:
                return job

        return None

    def get_utilization(self):
        # TODO
        return

    def __str__(self):
        return "task {0}: (Φ,T,C,D,∆) = ({1}, {2}, {3}, {4}, {5})".format(self.id, self.offset, self.period, self.wcet,
                                                                          self.relativeDeadline, self.sections)


class Job(object):
    def __init__(self, task, job_id, release_time):
        # TODO
        self.task = task
        self.id = job_id
        self.releaseTime = release_time
        self.deadline = release_time + task.relativeDeadline
        return

    def get_resource_held(self):
        """the resources that it's currently holding"""
        # TODO
        return

    def get_recourse_waiting(self):
        """a resource that is being waited on, but not currently executing"""
        # TODO
        return

    def get_remaining_section_time(self):
        # TODO
        return

    def execute(self, time):
        # TODO
        return

    def execute_to_completion(self):
        # TODO
        return

    def is_completed(self):
        # TODO
        return

    def __str__(self):
        return "[{0}:{1}] released at {2} -> deadline at {3}".format(self.task.id, self.id, self.releaseTime,
                                                                     self.deadline)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "taskset.json"

    with open(file_path) as json_data:
        data = json.load(json_data)

    taskSet = TaskSet(data)

    taskSet.print_tasks()
    taskSet.print_jobs()
