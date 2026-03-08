# Swarm Memory System
import json
import os

class SwarmMemory:
    def __init__(self, storage_path="swarm_memory.json"):
        self.path = storage_path
        self.memory = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                return json.load(f)
        return {"sessions": [], "knowledge_base": {}}

    def save_session(self, session_data):
        self.memory["sessions"].append(session_data)
        self._persist()

    def _persist(self):
        with open(self.path, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def search_knowledge(self, query):
        # Basic keyword search
        return self.memory["knowledge_base"].get(query, "No historical data found.")
