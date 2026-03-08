# E.D.I.T.H Zenith: Tactical Architecture Guide 🛠️

This guide provides technical details for the **Multi-Agent Neural Swarm (MANS)** and the **Advanced Tactical Toolkit (ATT)**.

## 1. MANS Component Architecture
- **engine.py**: The central orchestrator for agent lifecycles and task dispatching.
- **blackboard.py**: Thread-safe shared memory for inter-agent communication.
- **scheduler.py**: Priority-queue-based task management.
- **base_agent.py**: Abstract base class for specialized tactical units.
- **factory.py**: Factory pattern for dynamic agent instantiation (Recon, Exploit, Defense, Analyst).
- **protocol.py**: Standardized JSON-based communication protocol for agent-to-agent talk.

## 2. ARTIFICIAL INTELLIGENCE (AI) Integration
- **agent.py**: The AI Strategist kernel that bridges neural logic to terminal and swarm commands.
- **system_prompt**: The AI is instructed to prefer tool calls (Payloads, CVEs, Swarms) over natural language.

## 3. Advanced Tactical Toolkit (ATT)
- **payload_gen.py**: Professional reverse-shell generation with base64/hex encoding options.
- **net_map_viz.py**: Processes scan results into graphical node-edge JSON for visualization.
- **cve_lookup.py**: Local vulnerability cross-referencing for offline research.
- **sniffer.py**: Passive network sniffing framework (Scapy integration).
- **scanner_pro.py**: Enhanced Nmap wrapper with NSE script support.
- **report_builder.py**: Generates professional mission reports in Markdown style.

## 4. Zenith UI/UX Design System
- **24px Grid**: Standardized spacing for all dashboard cards and side-nav elements.
- **QPainter Analytics**: Dynamic visualization of neural activity and kernel heartbeat.
- **Floating HUD**: Quick-Action bar for manual tactical command deployment.

---
*E.D.I.T.H Zenith - Architecture Documentation // Zenith Tactical Group*
