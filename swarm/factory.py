# Swarm Agent Factory
from .recon_agent import ReconAgent
from .exploit_agent import ExploitAgent
from .defense_agent import DefenseAgent
from .analyst_agent import AnalystAgent

class AgentFactory:
    @staticmethod
    def create_agent(agent_type, name, blackboard, kernel=None):
        mapping = {
            "recon": ReconAgent,
            "exploit": ExploitAgent,
            "defense": DefenseAgent,
            "analyst": AnalystAgent
        }
        
        agent_class = mapping.get(agent_type.lower())
        if agent_class:
            return agent_class(name, blackboard, kernel=kernel)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
