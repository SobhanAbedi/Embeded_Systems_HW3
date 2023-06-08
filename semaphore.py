# TODO Accommodate other method of resource management
class SemaphoreSet(object):
    def __init__(self, resources):
        self.semaphores = {}
        for resource in resources:
            self.semaphores[resource] = Semaphore(resource)

    def wait(self, resource, job) -> int:
        if resource == 0:
            return 0
        if resource in self.semaphores.keys():
            return self.semaphores[resource].wait(job)
        return -1

    def signal(self, resource, job) -> int:
        if resource == 0:
            return 0
        if resource in self.semaphores.keys():
            return self.semaphores[resource].signal(job)
        return -1


class Semaphore:
    def __init__(self, semaphore_id, lowest_priority=1000):
        self.semaphore_id = semaphore_id
        self.lowest_priority = lowest_priority
        self.priority = lowest_priority
        self.jobs = []
        self.owner = None
        self.taken = False

    def elevate_priority(self, priority):
        if priority < self.priority:
            self.priority = priority

    def wait(self, job) -> int:
        self.jobs.append(job)
        self.jobs.sort()
        self.priority = self.jobs[0].get_deadline()
        if self.taken is True:
            return -1
        self.owner = job
        self.taken = True
        return 0

    def signal(self, job) -> int:
        self.jobs.remove(job)
        if len(self.jobs) > 0:
            self.priority = self.jobs[0].get_deadline()
        else:
            self.priority = self.lowest_priority

        if self.owner == job:
            if len(self.jobs) > 0:
                self.owner = self.jobs[0]
                self.owner.unblock()
                return 1

            self.owner = None
            self.taken = False
            return 0
        return -1

    def is_taken(self) -> bool:
        return self.is_taken()

    def get_priority(self) -> int:
        return self.priority


EMPTY_SEM_SET = SemaphoreSet([])
