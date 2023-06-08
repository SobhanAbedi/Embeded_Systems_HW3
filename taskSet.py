from task import Task, EMPTY_TASK
from task import TaskSetJsonKeys as TSJK
from semaphore import Semaphore, SemaphoreSet


class TaskSetIterator:
    def __init__(self, task_set):
        self.taskSet = task_set
        self.index = 0
        self.keys = iter(task_set.tasks)

    def __next__(self) -> Task:
        key = next(self.keys)
        return self.taskSet.tasks[key]


class TaskSet(object):
    def __init__(self, data):
        self.jobs = []
        self.tasks = {}
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
        jobs = []

        if TSJK.KEY_RELEASETIMES in data:  # necessary for sporadic releases
            for job_release in data[TSJK.KEY_RELEASETIMES]:
                release_time = float(job_release[TSJK.KEY_RELEASETIMES_JOBRELEASE])
                task_id = int(job_release[TSJK.KEY_RELEASETIMES_TASKID])

                job = self.get_task_by_id(task_id).spawn_job(release_time)
                jobs.append(job)
        else:
            schedule_start_time = float(data[TSJK.KEY_SCHEDULE_START])
            schedule_end_time = float(data[TSJK.KEY_SCHEDULE_END])
            for task in self:
                t = max(task.offset, schedule_start_time)
                while t < schedule_end_time:
                    job = task.spawn_job(t, self.resources)
                    if job is not None:
                        jobs.append(job)

                    if task.period >= 0:
                        t += task.period  # periodic
                    else:
                        t = schedule_end_time  # aperiodic

        self.jobs = jobs

    def get_all_resources(self) -> list[int]:
        return self.resources

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
        for task in self:
            for job in task.get_jobs():
                print(job)
