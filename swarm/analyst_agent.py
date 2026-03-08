# Analyst Tactical Unit
from .base_agent import BaseAgent
import time

class AnalystAgent(BaseAgent):
    def __init__(self, name, blackboard):
        super().__init__(name, "analyst", blackboard)

    def execute(self, task):
        print(f"[ANALYST {self.name}] Parsing session data for final report...")
        time.sleep(3)
        data = self.blackboard.get_all()
        report = f"Session Report: {len(data)} observations recorded."
        self.blackboard.post("final_report", report, self.name)
        print(f"[ANALYST {self.name}] Report generated.")
