from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class LandingPage(QWidget):
    selection_made = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(40)

        title = QLabel("E.D.I.T.H")
        title.setStyleSheet("""
            font-size: 100px; 
            font-weight: bold; 
            color: #00A3FF; 
            font-family: 'Consolas';
            letter-spacing: 15px;
        """)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("NEURAL CYBERSECURITY KERNEL // v1.0")
        subtitle.setStyleSheet("font-size: 12px; color: #444; letter-spacing: 8px;")
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(30)

        win_btn = self.create_btn("POWERSHELL_CORE", "#00A3FF")
        win_btn.clicked.connect(lambda: self.selection_made.emit("powershell"))
        
        linux_btn = self.create_btn("WSL_LINUX_KERNEL", "#E95420")
        linux_btn.clicked.connect(lambda: self.selection_made.emit("wsl"))

        btn_layout.addWidget(win_btn)
        btn_layout.addWidget(linux_btn)
        layout.addLayout(btn_layout)

    def create_btn(self, text, color):
        btn = QPushButton(text)
        btn.setFixedSize(280, 80)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {color};
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas';
                border: 1px solid #222;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: black;
                border: 1px solid {color};
            }}
        """)
        return btn
