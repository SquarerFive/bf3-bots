from threading import Thread
import time

class TaskPoolConfig():
    def __init__(self, sleep_time:float = 0.5, awake_time:float = 0.01):
        self.sleep_time = sleep_time
        self.awake_time = awake_time

class TaskPool():
    def __init__(self, config : TaskPoolConfig):
        self.tasks = [] # lambda[]
        self.awake_interval = config.awake_time
        self.sleep_interval = config.sleep_time
        self.interval = self.sleep_interval
        self.should_stop = False
    
    def dequeue(self):
        print("D", self.tasks)
        old_tasks = self.tasks
        old_tasks[0]()
        self.tasks = old_tasks[1:]
        print("Q", self.tasks)
        print("tasks: ", len(self.tasks))

    def enqueue(self, task):
        self.tasks.append(task)

    def tick(self):
        if len(self.tasks) > 0:
            self.interval = self.awake_interval
            for t in self.tasks:
                t()
            self.tasks.clear()
        else:
            self.interval = self.sleep_interval

        time.sleep(self.interval)

    def run(self):
        while not self.should_stop:
            self.tick()

class ThreadPool():
    def __init__(self, threads=4, config : TaskPoolConfig = TaskPoolConfig(), task_pool_type : TaskPool = TaskPool):
        self.task_pools = []
        self.threads = []
        for i in range(threads):
            self.task_pools.append(task_pool_type(config=config))
            self.threads.append(
                Thread(target=self.task_pools[-1].run, daemon=True)
            )
        for thread in self.threads:
            thread.start()
    
    def enqueue(self, task):
        min_tasks = 999
        min_taskpool = None
        for taskPool in self.task_pools:
            if len(taskPool.tasks) < min_tasks:
                min_tasks = len(taskPool.tasks)
                min_taskpool = taskPool
        min_taskpool.enqueue(task)
