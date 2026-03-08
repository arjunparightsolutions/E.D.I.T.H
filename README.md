# E.D.I.T.H: Professional Agentic Cybersecurity OS

E.D.I.T.H is an advanced, industrial-grade agentic cybersecurity kernel designed for professional tactical operations. It features a "Docker-Desktop" style Mission Dashboard combined with a high-performance interactive terminal and a proactive AI strategist.

![Interface Mockup](https://via.placeholder.com/800x450.png?text=E.D.I.T.H+Cyberdeck+Interface)

## 🚀 Key Features

- **Mission Control Dashboard**: Real-time tracking of tactical objectives and neural strategic plans.
- **Tactical Terminal Interface**: Zero-lag interactive shell supporting both Windows PowerShell and WSL Linux kernels.
- **Proactive AI Strategic Kernel**: An agentic brain that not only suggests but **proactively executes** commands based on mission goals.
- **Command Intent Preview**: A dedicated HUD that explains AI intent before and during terminal execution.
- **Auto-Execute Toggle**: Switch between high-autonomy and human-in-the-loop tactical flows.
- **Neural Model Selector**: On-the-fly switching between GPT-4o and GPT-4o-mini.

## 🛠️ Installation & Setup

### Prerequisites
1.  **Python 3.10+** installed on Windows.
2.  **OpenAI API Key**.
3.  (Optional) **WSL** (Windows Subsystem for Linux) for the Linux Kernel experience.

### Step-by-Step Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/ArjunPAP/E.D.I.T.H.git
    cd E.D.I.T.H
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**:
    - Create a `.env` file in the root directory.
    - Add your OpenAI API key:
      ```env
      OPENAI_API_KEY=sk-...
      ```

4.  **Launch the System**:
    ```bash
    python main.py
    ```

## 🎮 How to Use

1.  **Boot**: Run `python main.py` and select either `POWERSHELL_CORE` or `WSL_LINUX_KERNEL`.
2.  **Directive**: In the **Strategist Thread**, transmit your tactical goal (e.g., "Analyze the local network for vulnerabilities").
3.  **Command & Control**:
    - Watch the **Mission Tasks** update with the breakdown.
    - Observe the **Tactical Preview** for the AI's intended command.
    - The terminal will execute the command and the results will be analyzed by the agent.

---

## 🎖️ Credits & Acknowledgements

- **Concept & Development**: Arjun P A, Right Solutions A.I
- **AI Models**: OpenAI (GPT-4o / GPT-4o-mini)
- **Neural Architecture**: Inspired by Google's Transformer Architecture
- **Terminal Rendering**: Powered by `pyte` and `pywinpty`
- **UI Framework Engine**: PyQt6 with `qdarktheme` styling

---

> [!IMPORTANT]
> This tool is intended for professional cybersecurity research and educational purposes only. Always ensure you have explicit permission before scanning any network or system.

© 2026 Arjun P A // Right Solutions A.I
