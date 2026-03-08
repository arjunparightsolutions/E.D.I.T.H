# Swarm Communication Protocol
import json

class SwarmProtocol:
    MSG_HANDSHAKE = "HELO"
    MSG_TASK_ASSIGN = "TASK"
    MSG_DATA_SHARE = "DATA"
    MSG_STATUS_UPDATE = "STAT"

    @staticmethod
    def format_message(msg_type, sender, payload):
        return json.dumps({
            "type": msg_type,
            "sender": sender,
            "data": payload
        })

    @staticmethod
    def parse_message(raw_msg):
        return json.loads(raw_msg)
