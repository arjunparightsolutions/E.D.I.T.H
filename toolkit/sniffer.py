# Passive Network Sniffer (Mock/Integration)
class PacketSniffer:
    def __init__(self):
        self.capturing = False
        self.data_buffer = []

    def start_capture(self, interface="any"):
        self.capturing = True
        print(f"[SNIFFER] Monitoring {interface}...")

    def stop_capture(self):
        self.capturing = False

    def get_recent_packets(self):
        # Simulated packet data
        import random
        if self.capturing:
            self.data_buffer.append(f"TCP {random.randint(1,255)}.{random.randint(1,255)}.1.1 -> 192.168.1.10 [PUSH]")
        return self.data_buffer[-10:]
