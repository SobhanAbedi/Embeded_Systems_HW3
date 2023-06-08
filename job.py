
class JobState:
    RUNNING = 0  # Currently executing on the processor
    CREATED = 1  # Job has been created but not released yet
    READY = 2  # Ready to run but Job of higher or equal priority is currently running
    BLOCKED = 3  # Job is waiting for some condition to be met to move to READY state
    SUSPENDED = 4  # Job is waiting for some other Job to unsuspend
    ABORTED = 5  # Job has a hard deadline, and it gets aborted if it misses its deadline


class Job(object):
    def __init__(self, task, resources, job_id=0, release_time=0):

        self.state = JobState.CREATED
        self.id = job_id
        self.releaseTime = release_time

        self.current_section = 0

        if task is not None and resources is not None:
            self.task = task
            self.resources = resources
            self.remaining_execution_time = self.task.wcet
            self.deadline = release_time + task.relativeDeadline
            self.sections = task.sections
        else:
            self.task = None
            self.resources = None
            self.remaining_execution_time = 0
            self.deadline = release_time
            self.sections = []

    def get_resources_held(self) -> int:
        """the resources that it's currently holding"""
        if self.state in [JobState.READY, JobState.RUNNING, JobState.SUSPENDED]:
            return self.sections[self.current_section][0]
        else:
            return 0

    def get_recourses_waiting(self) -> int:
        """a resource that is being waited on, but not currently executing"""
        if self.state == JobState.BLOCKED:
            return self.sections[self.current_section][0]
        else:
            return 0

    def get_deadline(self) -> int:
        return self.deadline

    def get_remaining_section_time(self) -> int:
        if self.remaining_execution_time > 0:
            return self.sections[self.current_section][1]
        else:
            return 0

    def execute(self, time):
        # TODO
        return

    def execute_to_completion(self):
        # TODO
        return

    def is_completed(self) -> bool:
        if self.remaining_execution_time > 0:
            return False
        else:
            return True

    def __str__(self) -> str:
        return "[{0}:{1}] released at {2} -> deadline at {3}".format(self.task.id, self.id, self.releaseTime,
                                                                     self.deadline)

    def __lt__(self, other) -> bool:
        if self.deadline < other.get_deadline():
            return True
        return False

    def __le__(self, other) -> bool:
        if self.deadline <= other.get_deadline():
            return True
        return False

    def __eq__(self, other) -> bool:
        if self.deadline == other.get_deadline():
            return True
        return False

    def __ge__(self, other) -> bool:
        if self.deadline >= other.get_deadline():
            return True
        return False

    def __gt__(self, other) -> bool:
        if self.deadline > other.get_deadline():
            return True
        return False


EMPTY_JOB = Job(None, None)
