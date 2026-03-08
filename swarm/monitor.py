# Swarm UI Monitor Bridge
class SwarmMonitor:
    def __init__(self, engine, ui_callback):
        self.engine = engine
        self.ui_callback = ui_callback

    def get_swarm_status(self):
        status = []
        for aid, agent in self.engine.agents.items():
            status.append({
                "id": aid,
                "name": agent.name,
                "type": agent.type,
                "status": "BUSY" if not agent.idle else "IDLE",
                "task": agent.current_task if agent.current_task else "NONE"
            })
        return status

    def update_ui(self):
        if self.ui_callback:
            self.ui_callback(self.get_swarm_status())
