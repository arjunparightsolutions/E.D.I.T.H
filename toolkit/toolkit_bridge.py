# Advanced Tactical Toolkit (ATT) Integration Bridge
from .payload_gen import PayloadGenerator
from .net_map_viz import NetworkMapper
from .cve_lookup import CVELookup
from .sniffer import PacketSniffer
from .encoder import AdvancedEncoder
from .scanner_pro import ScannerPro
from .report_builder import ReportBuilder
from .credential_mgr import CredentialManager

class ToolkitBridge:
    def __init__(self, terminal=None):
        self.payload_gen = PayloadGenerator()
        self.net_map = NetworkMapper()
        self.cve_db = CVELookup()
        self.sniffer = PacketSniffer()
        self.scanner = ScannerPro(terminal)
        self.report = ReportBuilder()
        self.vault = CredentialManager()
        self.encoder = AdvancedEncoder()

    def handle_request(self, tool_name, *args):
        # Main entry point for AI/UI tool calls
        if tool_name == "payload":
            return self.payload_gen.generate(*args)
        elif tool_name == "cve":
            return self.cve_db.search(*args)
        elif tool_name == "encode":
            return self.encoder.encode(*args)
        elif tool_name == "report":
            return self.report.generate_markdown(*args)
        return f"ERROR: '{tool_name}' not active in current kernel."
