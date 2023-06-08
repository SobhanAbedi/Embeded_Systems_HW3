from job import Job, EMPTY_JOB
from task import Task, EMPTY_TASK
from task import TaskSetJsonKeys as TSJK
from semaphore import Semaphore, SemaphoreSet


class EventType:
    RELEASE = 0
    DEADLINE = 1


class TaskSetIterator:
    def __init__(self, task_set):
        self.taskSet = task_set
        self.index = 0
        self.keys = iter(task_set.tasks)

    def __next__(self) -> Task:
        key = next(self.keys)
        return self.taskSet.tasks[key]


def add_job(jobs: list[Job], events: dict[float, list[tuple[EventType, Job]]], job: Job, release_time: float, schedule_end_time: float):
    jobs.append(job)
    deadline = job.get_deadline()
    if release_time not in events.keys():
        events[release_time] = []
    events[release_time].append((EventType.RELEASE, job))
    if deadline <= schedule_end_time:
        if deadline not in events.keys():
            events[deadline] = []
        events[deadline].append((EventType.DEADLINE, job))


class TaskSet(object):
    def __init__(self, data):
        self.jobs: list[Job] = []
        self.tasks: dict[int, Task] = {}
        self.events: dict[float, list[tuple[EventType, Job]]] = {}
        self.event_list: list[float] = []
        self.parse_data_to_tasks(data)

        semaphores = {}
        for task_id in self.tasks.keys():
            resources = self.tasks[task_id].get_all_resources()
            for resource in resources:
                semaphores[resource] = 1

        self.resources = list(semaphores.keys())
        self.resources.sort()

        self.build_job_releases(data)

    def parse_data_to_tasks(self, data) -> None:
        task_set = {}

        for task_data in data[TSJK.KEY_TASKSET]:
            task = Task(task_data)

            if task.id in task_set:
                print("Error: duplicate task ID: {0}".format(task.id))
                return

            if task.period < 0 and task.relativeDeadline < 0:
                print("Error: aperiodic task must have positive relative deadline")
                return

            task_set[task.id] = task

        self.tasks = task_set

    def build_job_releases(self, data) -> None:
        jobs: list[Job] = []
        events: dict[float, list[tuple[EventType, Job]]] = {}
        schedule_start_time = float(data[TSJK.KEY_SCHEDULE_START])
        schedule_end_time = float(data[TSJK.KEY_SCHEDULE_END])
        if TSJK.KEY_RELEASETIMES in data:  # necessary for sporadic releases
            for job_release in data[TSJK.KEY_RELEASETIMES]:
                release_time = float(job_release[TSJK.KEY_RELEASETIMES_JOBRELEASE])
                task_id = int(job_release[TSJK.KEY_RELEASETIMES_TASKID])

                if release_time >= schedule_start_time:
                    job = self.get_task_by_id(task_id).spawn_job(release_time)
                    add_job(jobs, events, job, release_time, schedule_end_time)
        else:
            for task in self:
                t = max(task.offset, schedule_start_time)
                while t < schedule_end_time:
                    job: Job = task.spawn_job(t)
                    if job is not EMPTY_JOB:
                        add_job(jobs, events, job, t, schedule_end_time)

                    if task.period >= 0:
                        t += task.period  # periodic
                    else:
                        t = schedule_end_time  # aperiodic

        if schedule_end_time not in events.keys():
            events[schedule_end_time] = []

        self.jobs = jobs
        self.events = events
        self.event_list = list(self.events.keys())
        self.event_list.sort()

    def get_all_resources(self) -> list[int]:
        return self.resources

    def get_events(self) -> dict[float, list[tuple[EventType, Job]]]:
        return self.events

    def get_event_list(self) -> list[float]:
        return self.event_list

    def __contains__(self, elt) -> bool:
        return elt in self.tasks

    def __iter__(self) -> object:
        return TaskSetIterator(self)

    def __len__(self) -> int:
        return len(self.tasks)

    def get_task_by_id(self, task_id) -> Task:
        if task_id in self.tasks.keys():
            return self.tasks[task_id]
        return EMPTY_TASK

    def print_tasks(self) -> None:
        print("\nTask Set:")
        for task in self:
            print(task)

    def print_jobs(self) -> None:
        print("\nJobs:")
        for job in self.jobs:
            print(job)

    def print_events(self) -> None:
        print("\nEvents:")
        for event_time in self.event_list:
            print(f'Events at {event_time}')
            for event in self.events[event_time]:
                if event[0] == EventType.RELEASE:
                    print("Release of " + str(event[1]))
                else:
                    print("Deadline of " + str(event[1]))
