# Abstract Base Class for all Swarm Agents
import threading
import time

class BaseAgent:
    def __init__(self, name, agent_type, blackboard, kernel=None):
        self.id = None
        self.name = name
        self.type = agent_type
        self.blackboard = blackboard
        self.kernel = kernel
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
            self.log(f"[SWARM_AGENT] {self.name} ({self.type.upper()}) ACTIVE // TASK: {self.current_task}")
            self.execute(self.current_task)
        finally:
            self.idle = True
            self.current_task = None
            self.log(f"[SWARM_AGENT] {self.name} ({self.type.upper()}) IDLE // CYCLE_COMPLETE")

    def log(self, message):
        # Log to PTY/Terminal if available
        if self.kernel:
            self.kernel.data_received.emit(f"\r\n{message}\r\n")
        else:
            print(message)

    def execute(self, task):
        # Override in specialized units
        pass

    def stop(self):
        self.stopped = True
