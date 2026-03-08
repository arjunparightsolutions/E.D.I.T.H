from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFrame, QScrollArea, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen

class LandingPage(QWidget):
    selection_made = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setContentsMargins(50, 50, 50, 50)
        
        self.setStyleSheet("background-color: #080809;")
        
        # --- ZENITH BOOT STATE ---
        self.init_boot_ui()
        
        self.boot_timer = QTimer(self)
        self.boot_timer.timeout.connect(self.update_boot_logs)
        self.boot_step = 0
        self.boot_logs = [
            "[OK] TITAN_BIOS_V2.5 INITIALIZING...",
            "[OK] CHECKING RAM: 64GB DETECTED",
            "[OK] LOADING MANS_ENGINE CORE...",
            "[OK] SYNCHRONIZING NEURAL_BLACKBOARD...",
            "[WARN] PERIPHERAL_SCAN: HUB_NOT_FOUND",
            "[OK] CONNECTING TO STRATEGIC_BRIDGE...",
            "[OK] MOUNTING ATT_TOOLKIT_V1.0...",
            "[OK] ESTABLISHING TACTICAL_PTY_SOCKETS...",
            "[OK] DEPLOYING GUARDIAN_SAFETY_GOVERNOR...",
            "[OK] KERNEL_INTEGRITY: 100%",
            "--- SYSTEM READY ---"
        ]
        self.boot_timer.start(300)

    def init_boot_ui(self):
        self.boot_frame = QFrame()
        self.boot_layout = QVBoxLayout(self.boot_frame)
        self.boot_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.log_area = QScrollArea()
        self.log_area.setWidgetResizable(True)
        self.log_area.setStyleSheet("background: transparent; border: none;")
        self.log_widget = QWidget()
        self.log_vbox = QVBoxLayout(self.log_widget)
        self.log_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.log_area.setWidget(self.log_widget)
        self.boot_layout.addWidget(self.log_area)
        
        self.prog = QProgressBar()
        self.prog.setFixedHeight(4)
        self.prog.setStyleSheet("""
            QProgressBar { background: #111; border: none; border-radius: 2px; }
            QProgressBar::chunk { background: #00A3FF; border-radius: 2px; }
        """)
        self.boot_layout.addWidget(self.prog)
        
        self.layout.addWidget(self.boot_frame)

    def update_boot_logs(self):
        if self.boot_step < len(self.boot_logs):
            lbl = QLabel(self.boot_logs[self.boot_step])
            lbl.setStyleSheet("font-family: 'JetBrains Mono', 'Consolas'; font-size: 13px; color: #00FF41;")
            self.log_vbox.addWidget(lbl)
            self.boot_step += 1
            self.prog.setValue(int((self.boot_step / len(self.boot_logs)) * 100))
        else:
            self.boot_timer.stop()
            QTimer.singleShot(500, self.transition_to_selection)

    def transition_to_selection(self):
        self.boot_frame.hide()
        self.init_selection_ui()

    def init_selection_ui(self):
        self.select_frame = QFrame()
        layout = QVBoxLayout(self.select_frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(50)

        title = QLabel("E.D.I.T.H // ZENITH")
        title.setStyleSheet("""
            font-size: 80px; 
            font-weight: 900; 
            color: #FFFFFF; 
            font-family: 'Inter', sans-serif;
            letter-spacing: 20px;
        """)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("NEURAL_TACTICAL_DEPLOYMENT_HUB_V2.5")
        subtitle.setStyleSheet("font-size: 10px; color: #00A3FF; font-weight: 800; letter-spacing: 12px;")
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(40)

        win_btn = self.create_btn("POWERSHELL_KERNAL", "#00A3FF")
        win_btn.clicked.connect(lambda: self.selection_made.emit("powershell"))
        
        linux_btn = self.create_btn("WSL_LINUX_PRO", "#00FF41")
        linux_btn.clicked.connect(lambda: self.selection_made.emit("wsl"))

        btn_layout.addWidget(win_btn)
        btn_layout.addWidget(linux_btn)
        layout.addLayout(btn_layout)
        
        self.layout.addWidget(self.select_frame)

    def create_btn(self, text, color):
        btn = QPushButton(text)
        btn.setFixedSize(300, 90)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.02);
                color: {color};
                font-size: 12px;
                font-weight: 900;
                font-family: 'JetBrains Mono';
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: black;
                border: 1px solid {color};
            }}
        """)
        return btn
