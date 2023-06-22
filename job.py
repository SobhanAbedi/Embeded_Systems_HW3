from __future__ import annotations
from semaphore import SemaphoreSet, EMPTY_SEM_SET
from copy import deepcopy


class JobState:
    RUNNING = 0  # Currently executing on the processor
    CREATED = 1  # Job has been created but not released yet
    READY = 2  # Ready to run but Job of higher or equal priority is currently running
    BLOCKED = 3  # Job is waiting for some condition to be met to move to READY state
    SUSPENDED = 4  # Job is waiting for some other Job to unsuspend
    ENDED = 5
    ABORTED = 6  # Job has a hard deadline, and it gets aborted if it misses its deadline


class Job(object):
    def __init__(self, task, job_id=0, release_time=0):

        self.state = JobState.CREATED
        self.id = job_id
        self.releaseTime = release_time
        self.readyQueue: list[Job] = []
        self.waitingQueue: list[Job] = []
        self.currSectionIdx = 0
        self.semaphores: SemaphoreSet = EMPTY_SEM_SET
        self.gotLock: bool = False
        self.remaining_execution_time = 0
        self.deadline = release_time
        self.originalPriority = 0
        self.priority = 0
        self.sections = []

        if task is not None:
            self.task = task
            self.remaining_execution_time = self.task.wcet
            self.deadline = release_time + task.relativeDeadline
            self.originalPriority = task.relativeDeadline
            self.priority = self.originalPriority
            self.sections = deepcopy(task.sections)
        else:
            self.task = None

    def get_resources_held(self) -> int:
        """the resources that it's currently holding"""
        if self.state in [JobState.READY, JobState.RUNNING, JobState.SUSPENDED]:
            return self.sections[self.currSectionIdx][0]
        else:
            return 0

    def get_recourses_waiting(self) -> int:
        """a resource that is being waited on, but not currently executing"""
        if self.state == JobState.BLOCKED:
            return self.sections[self.currSectionIdx][0]
        else:
            return 0

    def get_release_time(self) -> float:
        return self.releaseTime

    def get_deadline(self) -> float:
        return self.deadline

    def get_priority(self) -> float:
        return self.priority

    def update_queue(self):
        if self.state == JobState.READY:
            self.readyQueue.sort()
        elif self.state == JobState.BLOCKED:
            self.waitingQueue.sort()

    def elevate_priority(self, new_priority: float) -> None:
        if new_priority < self.priority:
            self.priority = new_priority
            self.update_queue()
            # print(f"Priority of {self.short_form()} elevated to {new_priority}")

    def revert_priority(self, new_priority: float) -> None:
        if 0 <= new_priority < self.originalPriority:
            self.priority = new_priority
            self.update_queue()
            # print(f"Priority of {self.short_form()} reverted to {new_priority}")
        else:
            self.priority = self.originalPriority
            self.update_queue()
            # print(f"Priority of {self.short_form()} reverted to original {self.originalPriority}")

    def get_remaining_section_time(self) -> int:
        if self.remaining_execution_time > 0:
            return self.sections[self.currSectionIdx][1]
        else:
            return 0

    def release(self, semaphores: SemaphoreSet, ready_queue: list[Job], waiting_queue: list[Job]) -> None:
        self.semaphores = semaphores
        self.readyQueue: list[Job] = ready_queue
        self.waitingQueue: list[Job] = waiting_queue
        self.readyQueue.append(self)
        self.readyQueue.sort()
        self.state = JobState.READY

    def end(self) -> None:
        if self.state == JobState.READY:
            self.readyQueue.remove(self)
        elif self.state == JobState.BLOCKED:
            self.semaphores.abandon(self.sections[self.currSectionIdx][0], self)
            self.waitingQueue.remove(self)
        self.readyQueue = []
        self.waitingQueue = []
        self.semaphores = EMPTY_SEM_SET
        if self.remaining_execution_time > 0:
            self.state = JobState.ABORTED
        else:
            self.state = JobState.ENDED

    def unblock(self) -> None:
        self.waitingQueue.remove(self)
        self.readyQueue.append(self)
        self.state = JobState.READY
        self.readyQueue.sort()
        self.gotLock = True

    def execute(self, time: float) -> tuple[float, int]:
        # print(f'Execute ({time}) job {self.task.id}:{self.id}')
        passed_time = 0
        curr_section = self.sections[self.currSectionIdx]
        progression_time = min(curr_section[1], time)
        resource = curr_section[0]
        if self.gotLock or self.semaphores.wait(resource, self) == 0:
            self.gotLock = True
            # print(f'got lock {curr_section[0]}')
            self.remaining_execution_time -= progression_time
            curr_section[1] -= progression_time
            if curr_section[1] == 0:
                self.currSectionIdx += 1
                res = self.semaphores.signal(resource, self)
                if res >= 0:
                    self.gotLock = False
                    # print(f'freed lock {curr_section[0]}')
                else:
                    print("!!!Freeing A Semaphore that was Not taken!!!")

        else:
            self.readyQueue.remove(self)
            self.waitingQueue.append(self)
            self.state = JobState.BLOCKED
            progression_time = 0

        if self.remaining_execution_time == 0:
            # if self.gotLock:
            #     self.semaphores.signal(curr_section[0], self)
            self.end()
        return progression_time, resource

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

    def short_form(self) -> str:
        return f'Job[{self.task.id}:{self.id}]'

    def __lt__(self, other: Job) -> bool:
        if self.priority < other.get_priority():
            return True
        return False

    def __le__(self, other: Job) -> bool:
        if self.priority <= other.get_priority():
            return True
        return False

    def __ge__(self, other: Job) -> bool:
        if self.priority >= other.get_priority():
            return True
        return False

    def __gt__(self, other: Job) -> bool:
        if self.priority > other.get_priority():
            return True
        return False


EMPTY_JOB = Job(None)
