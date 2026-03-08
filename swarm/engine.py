import threading
import time
import uuid

class SwarmEngine:
    def __init__(self, main_kernel=None):
        self.kernel = main_kernel
        self.agents = {}
        self.blackboard = None
        self.scheduler = None
        self.running = False
        self.lock = threading.Lock()

    def start(self, blackboard, scheduler):
        self.blackboard = blackboard
        self.scheduler = scheduler
        self.running = True
        threading.Thread(target=self._orchestration_loop, daemon=True).start()
        print("[SWARM] Engine Online.")

    def register_agent(self, agent):
        with self.lock:
            agent_id = str(uuid.uuid4())[:8]
            self.agents[agent_id] = agent
            agent.id = agent_id
            print(f"[SWARM] Agent {agent.name} (ID: {agent_id}) Registered.")
            return agent_id

    def _orchestration_loop(self):
        while self.running:
            # Check for tasks in scheduler and dispatch to agents
            task = self.scheduler.get_next_task()
            if task:
                self.dispatch(task)
            time.sleep(1)

    def dispatch(self, task):
        # Logic to find the best agent for the task
        target_type = task.get("target_type")
        for aid, agent in self.agents.items():
            if agent.type == target_type and agent.is_idle():
                agent.assign(task)
                return True
        return False

    def stop(self):
        self.running = False
