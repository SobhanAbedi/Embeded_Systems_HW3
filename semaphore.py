class SemaphoreAP:
    SIMPLE = 0
    HLP = 1
    PIP = 2


class SemaphoreSet(object):
    def __init__(self, resources: list[int], lowest_priority=1000, access_protocol: SemaphoreAP = SemaphoreAP.SIMPLE,
                 resources_highest_priority: dict[int, float] = {}):
        self.semaphores = {}
        self.lowestPriority = lowest_priority
        self.accessProtocol = access_protocol
        self.resourcesHighestPriority = resources_highest_priority.copy()
        for resource in resources:
            self.semaphores[resource] = Semaphore(resource, lowest_priority)
            if self.accessProtocol in [SemaphoreAP.HLP] and \
                    (resource not in self.resourcesHighestPriority or self.resourcesHighestPriority[resource] == -1):
                self.resourcesHighestPriority[resource] = self.lowestPriority

    def wait(self, resource, job) -> int:
        if resource == 0:
            return 0
        if resource in self.semaphores.keys():
            res = self.semaphores[resource].wait(job)

            if self.accessProtocol == SemaphoreAP.HLP:
                job.elevate_priority(self.resourcesHighestPriority[resource])
            elif self.accessProtocol == SemaphoreAP.PIP:
                if res == -1:
                    self.semaphores[resource].elevate_priorities()

            return res
        return -1

    def signal(self, resource, job) -> int:
        if resource == 0:
            return 0
        if resource in self.semaphores.keys():
            res = self.semaphores[resource].signal(job)

            if self.accessProtocol == SemaphoreAP.HLP:
                job.revert_priority(-1)
            elif self.accessProtocol == SemaphoreAP.PIP:
                if res >= 0:
                    job.revert_priority(-1)
                    self.semaphores[resource].revert_priorities()

            return res
        return -1

    def abandon(self, resource, job) -> int:
        if resource == 0:
            return 0
        if resource in self.semaphores.keys():
            res = self.semaphores[resource].abandon(job)

            if self.accessProtocol == SemaphoreAP.HLP:
                job.revert_priority(-1)
            elif self.accessProtocol == SemaphoreAP.PIP:
                if res >= 0:
                    job.revert_priority(-1)
                    self.semaphores[resource].revert_priorities()

            return res
        return -1


class Semaphore:
    def __init__(self, semaphore_id, lowest_priority=1000):
        self.semaphore_id = semaphore_id
        self.lowest_priority = lowest_priority
        self.priority = lowest_priority
        self.elevated_priority = lowest_priority
        self.jobs = []
        self.owner = None
        self.taken = False

    def elevate_priorities(self):
        if self.priority < self.elevated_priority:
            self.elevated_priority = self.priority
            for job in self.jobs:
                job.elevate_priority(self.priority)

    def revert_priorities(self):
        if self.elevated_priority < self.priority:
            self.elevated_priority = self.priority
            for job in self.jobs:
                job.revert_priority(self.priority)

    def wait(self, job) -> int:
        self.jobs.append(job)
        self.jobs.sort()
        self.priority = self.jobs[0].get_priority()
        if self.taken is True:
            return -1
        self.owner = job
        self.taken = True
        return 0

    def signal(self, job) -> int:
        self.jobs.remove(job)
        if self.owner == job:
            if len(self.jobs) > 0:
                self.owner = self.jobs[0]
                self.priority = self.owner.get_priority()
                self.owner.unblock()
                return 1

            self.owner = None
            self.priority = self.lowest_priority
            self.taken = False
            return 0
        return -1

    def abandon(self, job) -> int:
        if job in self.jobs:
            if self.owner == job:
                return self.signal(job)
            self.jobs.remove(job)
            self.priority = self.jobs[0].get_priority()
            return 1
        else:
            return -1

    def is_taken(self) -> bool:
        return self.is_taken()

    def get_priority(self) -> int:
        return self.priority


EMPTY_SEM_SET = SemaphoreSet([])
