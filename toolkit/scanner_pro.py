# Enhanced Nmap Pro Wrapper (NSE/Vuln-Discovery)
class ScannerPro:
    def __init__(self, terminal_bridge=None):
        self.terminal = terminal_bridge

    def full_scan(self, target):
        # Professional SYN scan with scripts
        cmd = f"nmap -v -sS -sC -sV --script=vuln {target}"
        if self.terminal:
            return self.terminal.execute(cmd)
        return f"DRY RUN: {cmd}"

    def stealth_scan(self, target):
        return f"nmap -sS -T2 -Pn {target}"
