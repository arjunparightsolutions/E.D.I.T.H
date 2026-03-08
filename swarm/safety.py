# Swarm Safety Governor
class SafetyGovernor:
    def __init__(self):
        self.blocked_commands = ["rm -rf /", "format", "del /s /q c:\\"]
        self.require_auth = ["exploit", "delete", "write"]

    def validate_action(self, agent_type, command):
        # 1. Check for dangerous commands
        for blocked in self.blocked_commands:
            if blocked in command.lower():
                return False, f"CRITICAL: Blocked dangerous command detected: {blocked}"
        
        # 2. Check for actions requiring auth
        for restricted in self.require_auth:
            if restricted in command.lower():
                return False, "AUTHORIZATION_REQUIRED: Sensitive action detected."
                
        return True, "VALIDATED"
