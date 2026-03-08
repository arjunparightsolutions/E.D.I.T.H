# Abstract Base Class for all Swarm Agents
import threading
import time

class BaseAgent:
    def __init__(self, name, agent_type, blackboard):
        self.id = None
        self.name = name
        self.type = agent_type
        self.blackboard = blackboard
        self.idle = True
        self.current_task = None
        self.stopped = False

    def is_idle(self):
        return self.idle

    def assign(self, task):
        self.idle = False
        self.current_task = task
        threading.Thread(target=self._run_task, daemon=True).start()

    def _run_task(self):
        try:
            print(f"[AGENT {self.name}] Starting Task: {self.current_task}")
            self.execute(self.current_task)
        finally:
            self.idle = True
            self.current_task = None
            print(f"[AGENT {self.name}] Task Completed.")

    def execute(self, task):
        # Override in specialized units
        pass

    def stop(self):
        self.stopped = True
