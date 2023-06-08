from job import Job, EMPTY_JOB


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


class Task(object):
    def __init__(self, task_dict):
        self.id = 0
        self.period = 0
        self.wcet = 0
        self.relativeDeadline = 0
        self.offset = 0
        self.sections = []
        if task_dict is not None:
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

    def get_all_resources(self) -> list[int]:
        semaphores = {}
        for section in self.sections:
            semaphores[section[0]] = 1

        resources = list(semaphores.keys())
        resources.sort()
        if resources[0] < 0:
            print("Invalid Resource ID")
        elif resources[0] == 0:
            resources.pop(0)
        return resources

    def spawn_job(self, release_time) -> Job:
        if self.lastReleasedTime > 0 and release_time < self.lastReleasedTime:
            print("INVALID: release time of job is not monotonic")
            return EMPTY_JOB

        if self.lastReleasedTime > 0 and release_time < self.lastReleasedTime + self.period:
            print("INVDALID: release times are not separated by period")
            return EMPTY_JOB

        self.lastJobId += 1
        self.lastReleasedTime = release_time

        job = Job(self, self.lastJobId, release_time)

        self.jobs.append(job)
        return job

    def get_jobs(self) -> list[Job]:
        return self.jobs

    def get_job_by_id(self, job_id) -> Job:
        if job_id > self.lastJobId:
            return EMPTY_JOB

        job = self.jobs[job_id - 1]
        if job.id == job_id:
            return job

        for job in self.jobs:
            if job.id == job_id:
                return job

        return EMPTY_JOB

    def get_utilization(self) -> float:
        # TODO
        return 0.0

    def __str__(self) -> str:
        return "task {0}: (Φ,T,C,D,∆) = ({1}, {2}, {3}, {4}, {5})".format(self.id, self.offset, self.period, self.wcet,
                                                                          self.relativeDeadline, self.sections)


EMPTY_TASK = Task(None)
