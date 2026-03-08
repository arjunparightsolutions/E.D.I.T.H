import sys
import os
import threading
import time
import json
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPlainTextEdit, QLabel, QPushButton, QHBoxLayout, 
                             QStackedWidget, QFrame, QMessageBox, QScrollArea, 
                             QLineEdit, QSplitter, QComboBox, QTextBrowser, 
                             QListWidget, QListWidgetItem, QSizePolicy, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QCoreApplication, QSize, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QTextCursor, QKeyEvent, QColor, QIcon, QAction, QPainter, QLinearGradient, QBrush, QPen
import qdarktheme
from winpty import PtyProcess
import pyte
from agent import EdithAgent
from task_manager import TaskManager
from dotenv import load_dotenv

load_dotenv()

# --- APEX PROFESSIONAL DESIGN SYSTEM ---

STYLESHEET = """
QMainWindow {
    background-color: #0A0A0B;
}

#Sidebar {
    background-color: #0F0F11;
    border-right: 1px solid #1E1E22;
    min-width: 80px;
    max-width: 80px;
}

#TopToolbar {
    background-color: #0F0F11;
    border-bottom: 1px solid #1E1E22;
    min-height: 65px;
}

#DashboardCard {
    background-color: rgba(30, 30, 35, 0.4);
    border: 1px solid #2A2A30;
    border-radius: 12px;
}

#DashboardTitle {
    color: #4A4A50;
    font-weight: 800;
    font-size: 9px;
    letter-spacing: 2px;
    margin-bottom: 10px;
}

#StatusBadge {
    background-color: rgba(0, 163, 255, 0.1);
    color: #00A3FF;
    padding: 6px 12px;
    border: 1px solid rgba(0, 163, 255, 0.3);
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
}

#ChatInput {
    background-color: #1A1A1D;
    color: #FFFFFF;
    border: 1px solid #2A2A30;
    border-radius: 8px;
    padding: 14px;
    font-size: 13px;
    font-family: 'Inter', sans-serif;
}

#ChatInput:focus {
    border: 1px solid #00A3FF;
    background-color: #1E1E22;
}

#TerminalContainer {
    background-color: #050506;
    border: 1px solid #1E1E22;
    border-radius: 12px;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
}

QScrollBar::handle:vertical {
    background: #2A2A30;
    min-height: 30px;
    border-radius: 3px;
}

QProgressBar {
    border: none;
    background-color: #1E1E22;
    height: 4px;
    border-radius: 2px;
}

QProgressBar::chunk {
    background-color: #00A3FF;
    border-radius: 2px;
}
"""

class GlassCard(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("DashboardCard")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.title_label = QLabel(title.upper())
        self.title_label.setObjectName("DashboardTitle")
        self.layout.addWidget(self.title_label)
        
        self.content_layout = QVBoxLayout()
        self.layout.addLayout(self.content_layout)
        self.layout.addStretch()

class PulseIndicator(QWidget):
    def __init__(self, color="#00A3FF", parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.color = QColor(color)
        self.alpha = 255
        self.growing = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pulse)
        self.timer.start(50)

    def update_pulse(self):
        if self.growing:
            self.alpha += 10
            if self.alpha >= 255: self.growing = False
        else:
            self.alpha -= 10
            if self.alpha <= 50: self.growing = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QColor(self.color)
        c.setAlpha(self.alpha)
        painter.setBrush(QBrush(c))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 8, 8)

class SideNavButton(QPushButton):
    def __init__(self, icon_text, label, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 85)
        self.setCheckable(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(4)
        
        self.icon_lbl = QLabel(icon_text)
        self.icon_lbl.setStyleSheet("font-size: 22px; color: inherit;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.text_lbl = QLabel(label.upper())
        self.text_lbl.setStyleSheet("font-size: 9px; color: inherit; font-weight: 800; letter-spacing: 1.2px;")
        self.text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.text_lbl)
        
        self.update_style()
        self.toggled.connect(self.update_style)

    def update_style(self):
        if self.isChecked():
            self.setStyleSheet("background-color: #1A1A1D; color: #00A3FF; border-right: 2px solid #00A3FF;")
        else:
            self.setStyleSheet("background-color: transparent; color: #55555B; border: none;")

class TaskItem(QWidget):
    def __init__(self, title, status, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        
        dot = PulseIndicator("#00A3FF" if status == "in-progress" else "#50FA7B" if status == "done" else "#333338")
        layout.addWidget(dot)
        
        self.label = QLabel(title)
        self.label.setStyleSheet(f"color: {'#E0E0E6' if status != 'done' else '#55555B'}; font-size: 13px; font-weight: 500;")
        layout.addWidget(self.label)
        layout.addStretch()

class ChatBubble(QFrame):
    def __init__(self, text, is_ai=False):
        super().__init__()
        layout = QVBoxLayout(self)
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if is_ai:
            self.setStyleSheet("""
                ChatBubble {
                    background-color: rgba(0, 163, 255, 0.05);
                    border-radius: 12px;
                    border: 1px solid rgba(0, 163, 255, 0.1);
                    margin-right: 60px;
                    padding: 15px;
                }
                QLabel { color: #BBB; font-size: 14px; line-height: 1.5; font-family: 'Inter'; }
            """)
        else:
            self.setStyleSheet("""
                ChatBubble {
                    background-color: #1E1E22;
                    border-radius: 12px;
                    margin-left: 60px;
                    padding: 15px;
                    border: 1px solid #2A2A30;
                }
                QLabel { color: #FFF; font-size: 14px; font-family: 'Inter'; }
            """)
        layout.addWidget(self.label)

# --- APEX TERMINAL WIDGET ---

class TerminalWidget(QPlainTextEdit):
    key_pressed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)
        self.setFont(QFont("JetBrains Mono", 10))
        self.setStyleSheet("background-color: #050506; color: #00FF41; border: none; padding: 20px;")
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setUndoRedoEnabled(False)
        self.setCursorWidth(2)
        
        self.cols, self.rows = 120, 40
        self.screen = pyte.Screen(self.cols, self.rows)
        self.stream = pyte.Stream(self.screen)
        self.last_text = ""
        
        self.render_timer = QTimer(self)
        self.render_timer.timeout.connect(self.render_screen)
        self.render_timer.start(33)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        text = event.text()
        modifiers = event.modifiers()
        
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            ctrl_map = {Qt.Key.Key_C: "\x03", Qt.Key.Key_D: "\x04", Qt.Key.Key_L: "\x0c"}
            if key in ctrl_map: self.key_pressed.emit(ctrl_map[key]); return

        key_map = {
            Qt.Key.Key_Return: "\r\n", Qt.Key.Key_Enter: "\r\n",
            Qt.Key.Key_Backspace: "\b", Qt.Key.Key_Tab: "\t", Qt.Key.Key_Escape: "\x1b",
            Qt.Key.Key_Up: "\x1b[A", Qt.Key.Key_Down: "\x1b[B",
            Qt.Key.Key_Right: "\x1b[C", Qt.Key.Key_Left: "\x1b[D",
            Qt.Key.Key_Delete: "\x1b[3~", Qt.Key.Key_Home: "\x1b[H", Qt.Key.Key_End: "\x1b[F",
        }
        if key in key_map: self.key_pressed.emit(key_map[key])
        elif text: self.key_pressed.emit(text)

    def render_screen(self):
        lines = ["".join(self.screen.buffer[row][col].data for col in range(self.screen.columns))
                 for row in range(self.screen.lines)]
        full_text = "\n".join(lines).strip()
        if full_text != self.last_text:
            self.setPlainText(full_text)
            self.last_text = full_text
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        self.update_cursor_pos()

    def update_cursor_pos(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        for _ in range(self.screen.cursor.y): cursor.movePosition(QTextCursor.MoveOperation.Down)
        for _ in range(self.screen.cursor.x): cursor.movePosition(QTextCursor.MoveOperation.Right)
        self.setTextCursor(cursor)

# --- APEX MAIN OS ---

class EdithApp(QMainWindow):
    data_received = pyqtSignal(str)
    ai_response_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("E.D.I.T.H Apex - Tactical OS")
        self.resize(1700, 1000)
        self.setStyleSheet(STYLESHEET)
        
        self.task_mgr = TaskManager()
        self.agent = EdithAgent(terminal_bridge=self, task_manager=self.task_mgr)
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        from main_landing import LandingPage
        self.landing = LandingPage()
        self.landing.selection_made.connect(self.boot_system)
        self.stack.addWidget(self.landing)
        
        self.init_main_ui()
        self.setup_connections()
        
        self.pty = None
        self.alive = False

    def init_main_ui(self):
        self.main_view = QWidget()
        main_layout = QHBoxLayout(self.main_view)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- 1. PREMIUM SIDE NAV ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.btn_dash = SideNavButton("📊", "Dash")
        self.btn_term = SideNavButton("⌨️", "Term")
        self.btn_sett = SideNavButton("⚙️", "Config")
        self.btn_dash.setChecked(True)
        
        sidebar_layout.addWidget(self.btn_dash)
        sidebar_layout.addWidget(self.btn_term)
        sidebar_layout.addStretch()
        
        # Kernel Status Footer
        kernel_footer = QVBoxLayout()
        kernel_footer.setContentsMargins(0, 0, 0, 20)
        kernel_footer.setSpacing(5)
        self.pulse = PulseIndicator("#333338")
        kernel_footer.addWidget(self.pulse, alignment=Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel("KERNEL")
        lbl.setStyleSheet("font-size: 7px; color: #444; font-weight: 800; letter-spacing: 1px;")
        kernel_footer.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addLayout(kernel_footer)
        
        main_layout.addWidget(self.sidebar)
        
        # --- 2. CORE WORKSPACE ---
        workspace = QVBoxLayout()
        workspace.setContentsMargins(0, 0, 0, 0)
        workspace.setSpacing(0)
        
        # Apex Header
        header = QFrame()
        header.setObjectName("TopToolbar")
        header_l = QHBoxLayout(header)
        header_l.setContentsMargins(30, 0, 30, 0)
        
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title_box.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        logo = QLabel("E.D.I.T.H // APEX_KERNEL")
        logo.setStyleSheet("color: #FFFFFF; font-weight: 900; font-size: 16px; letter-spacing: 3px;")
        sub_logo = QLabel("NEURAL TACTICAL DEPLOYMENT V2.1")
        sub_logo.setStyleSheet("color: #00A3FF; font-weight: 800; font-size: 8px; letter-spacing: 4px;")
        title_box.addWidget(logo)
        title_box.addWidget(sub_logo)
        header_l.addLayout(title_box)
        
        header_l.addStretch()
        
        self.auto_exec_btn = QPushButton("AUTO-EXEC: ON")
        self.auto_exec_btn.setCheckable(True)
        self.auto_exec_btn.setChecked(True)
        self.auto_exec_btn.setFixedSize(140, 32)
        self.auto_exec_btn.setStyleSheet("""
            QPushButton { background-color: #1E1E22; color: #50FA7B; border: 1px solid #2A2A30; border-radius: 6px; font-weight: 800; font-size: 10px; }
            QPushButton:checked { background-color: rgba(80, 250, 123, 0.1); border: 1px solid #50FA7B; }
            QPushButton:!checked { background-color: rgba(255, 85, 85, 0.1); color: #FF5555; border: 1px solid #FF5555; }
        """)
        self.auto_exec_btn.toggled.connect(lambda c: self.auto_exec_btn.setText("AUTO-EXEC: ON" if c else "AUTO-EXEC: OFF"))
        header_l.addWidget(self.auto_exec_btn)

        self.model_box = QComboBox()
        self.model_box.addItems(["gpt-4o", "gpt-4o-mini"])
        self.model_box.setFixedSize(120, 32)
        self.model_box.setStyleSheet("background-color: #1A1A1D; color: #E0E0E6; border: 1px solid #2A2A30; padding: 0 10px; border-radius: 6px; font-size: 11px;")
        header_l.addWidget(QLabel("MODEL:", styleSheet="color: #444; font-size: 9px; margin-left: 20px; font-weight: 800;"))
        header_l.addWidget(self.model_box)
        
        self.status_badge = QLabel("OFFLINE")
        self.status_badge.setObjectName("StatusBadge")
        header_l.addWidget(self.status_badge)
        
        workspace.addWidget(header)
        
        # Primary Workspace Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("QSplitter::handle { background: #1E1E22; }")
        
        # --- LEFT: MISSION & STRATEGY ---
        left_pane = QWidget()
        left_pane_l = QVBoxLayout(left_pane)
        left_pane_l.setContentsMargins(30, 30, 15, 30)
        left_pane_l.setSpacing(25)
        
        # Top Row Dash
        dash_grid = QHBoxLayout()
        dash_grid.setSpacing(20)
        
        self.card_tasks = GlassCard("Tactical Objectives")
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("background: transparent; border: none;")
        self.card_tasks.content_layout.addWidget(self.task_list)
        
        self.card_swarm = GlassCard("Swarm Tactical HUD")
        self.swarm_list = QListWidget()
        self.swarm_list.setStyleSheet("background: transparent; border: none;")
        self.card_swarm.content_layout.addWidget(self.swarm_list)

        self.card_exec = GlassCard("Command Hud")
        self.card_exec.setFixedWidth(250)
        self.exec_preview = QLabel("NO_ACTIVE_STREAM")
        self.exec_preview.setStyleSheet("color: #444; font-family: 'JetBrains Mono'; font-size: 11px; font-weight: 800;")
        self.exec_preview.setWordWrap(True)
        self.card_exec.content_layout.addWidget(self.exec_preview)
        
        dash_grid.addWidget(self.card_tasks, stretch=3)
        dash_grid.addWidget(self.card_swarm, stretch=3)
        dash_grid.addWidget(self.card_exec, stretch=2)
        left_pane_l.addLayout(dash_grid, stretch=2)
        
        # AI Thread
        chat_card = GlassCard("Strategic Neural Bridge")
        cv = QVBoxLayout()
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("background: transparent; border: none;")
        self.chat_inner = QWidget()
        self.chat_vbox = QVBoxLayout(self.chat_inner)
        self.chat_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_inner.setStyleSheet("background: transparent;")
        self.chat_scroll.setWidget(self.chat_inner)
        cv.addWidget(self.chat_scroll)
        
        input_container = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setObjectName("ChatInput")
        self.chat_input.setPlaceholderText("Broadcast Mission objective...")
        self.chat_input.returnPressed.connect(self.handle_chat)
        input_container.addWidget(self.chat_input)
        
        cv.addLayout(input_container)
        chat_card.content_layout.addLayout(cv)
        left_pane_l.addWidget(chat_card, stretch=5)
        
        # --- RIGHT: DEPLOYMENT & LOGS ---
        right_pane = QWidget()
        right_pane_l = QVBoxLayout(right_pane)
        right_pane_l.setContentsMargins(15, 30, 30, 30)
        right_pane_l.setSpacing(25)
        
        # Strategy View
        plan_card = GlassCard("Deployment Blueprint")
        plan_card.setFixedHeight(250)
        self.plan_view = QTextBrowser()
        self.plan_view.setStyleSheet("background: transparent; border: none; color: #AAA; font-size: 12px; line-height: 1.6;")
        plan_card.content_layout.addWidget(self.plan_view)
        right_pane_l.addWidget(plan_card)
        
        # Terminal Pane
        term_frame = QFrame()
        term_frame.setObjectName("TerminalContainer")
        term_layout = QVBoxLayout(term_frame)
        term_layout.setContentsMargins(0, 0, 0, 0)
        
        term_header = QFrame()
        term_header.setFixedHeight(40)
        term_header.setStyleSheet("background-color: #0F0F11; border-bottom: 1px solid #1E1E22;")
        tl = QHBoxLayout(term_header)
        tl.setContentsMargins(20, 0, 20, 0)
        
        term_ico = QLabel("⌨️")
        term_ico.setStyleSheet("font-size: 14px;")
        tl.addWidget(term_ico)
        tl.addWidget(QLabel("TACTICAL_KERNAL_THREAD", styleSheet="color: #666; font-size: 10px; font-weight: 900; letter-spacing: 1px;"))
        tl.addStretch()
        
        self.agent_status = QLabel("IDLE")
        self.agent_status.setStyleSheet("color: #00A3FF; font-size: 10px; font-weight: 900; background: rgba(0, 163, 255, 0.1); padding: 4px 8px; border-radius: 4px;")
        tl.addWidget(self.agent_status)
        term_layout.addWidget(term_header)
        
        self.terminal = TerminalWidget()
        self.terminal.key_pressed.connect(self.send_to_pty)
        term_layout.addWidget(self.terminal)
        right_pane_l.addWidget(term_frame, stretch=1)

        self.splitter.addWidget(left_pane)
        self.splitter.addWidget(right_pane)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        
        workspace.addWidget(self.splitter)
        main_layout.addLayout(workspace)
        self.stack.addWidget(self.main_view)

    def setup_connections(self):
        self.data_received.connect(self.terminal.stream.feed)
        self.ai_response_ready.connect(self.post_ai_msg)
        self.task_mgr.task_updated.connect(self.sync_tasks)
        self.task_mgr.plan_updated.connect(self.plan_view.setMarkdown)
        
        self.swarm_timer = QTimer(self)
        self.swarm_timer.timeout.connect(self.sync_swarm)
        self.swarm_timer.start(1000)

    def boot_system(self, shell):
        self.alive = True
        self.status_badge.setText(f"KERNEL: {shell.upper()}")
        self.status_badge.setStyleSheet("background-color: #00A3FF; color: black; font-weight: 800; border-radius: 6px; padding: 6px 15px;")
        self.pulse.color = QColor("#00A3FF")
        try:
            cmd = "powershell.exe" if shell == "powershell" else "wsl.exe"
            self.pty = PtyProcess.spawn(cmd, dimensions=(self.terminal.rows, self.terminal.cols))
            threading.Thread(target=self.read_pty, daemon=True).start()
            self.stack.setCurrentIndex(1)
            self.post_ai_msg("Neural bridge synchronized. Kernel online. Ready for tactical directives.")
        except Exception as e:
            QMessageBox.critical(self, "Boot Failure", str(e))

    def handle_chat(self):
        txt = self.chat_input.text().strip()
        if not txt: return
        self.chat_input.clear()
        self.add_bubble(txt, False)
        self.set_agent_status("STRATEGIZING")
        threading.Thread(target=lambda: self.ai_response_ready.emit(self.agent.chat(txt)), daemon=True).start()

    def post_ai_msg(self, text):
        self.set_agent_status("READY")
        self.add_bubble(text, True)

    def set_agent_status(self, text):
        self.agent_status.setText(text.upper())
        if text.upper() in ["EXECUTING", "STRATEGIZING"]:
            self.pulse.color = QColor("#FF5555" if "EXEC" in text.upper() else "#00A3FF")
        else:
            self.pulse.color = QColor("#00A3FF")

    def add_bubble(self, text, is_ai):
        self.chat_vbox.addWidget(ChatBubble(text, is_ai))
        QCoreApplication.processEvents()
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())

    def sync_tasks(self):
        self.task_list.clear()
        for t in self.task_mgr.tasks:
            item = QListWidgetItem()
            widget = TaskItem(t['title'], t['status'])
            item.setSizeHint(widget.sizeHint())
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, widget)

    def sync_swarm(self):
        self.swarm_list.clear()
        for aid, agent in self.agent.swarm_engine.agents.items():
            status_text = f"[{agent.type.upper()}] {agent.name} - {'BUSY' if not agent.idle else 'IDLE'}"
            item = QListWidgetItem()
            widget = TaskItem(status_text, "in-progress" if not agent.idle else "todo")
            item.setSizeHint(widget.sizeHint())
            self.swarm_list.addItem(item)
            self.swarm_list.setItemWidget(item, widget)

    def execute(self, cmd):
        self.set_agent_status("EXECUTING")
        self.exec_preview.setText(f"> {cmd}")
        self.exec_preview.setStyleSheet("color: #00FF41; font-family: 'JetBrains Mono'; font-size: 11px; font-weight: 800;")
        
        if self.auto_exec_btn.isChecked():
            self.send_to_pty(cmd + "\r\n")
            time.sleep(2.0)
            self.set_agent_status("ANALYZING")
            return self.get_screen()
        else:
            self.set_agent_status("WAITING_AUTH")
            return "AUTO-EXEC DISABLED. MANUAL OVERRIDE REQUIRED."

    def get_screen(self): 
        lines = ["".join(self.terminal.screen.buffer[row][col].data for col in range(self.terminal.screen.columns))
                 for row in range(self.terminal.screen.lines)]
        return "\n".join(lines).strip()

    def send_to_pty(self, d): 
        if self.pty: 
            try: self.pty.write(d)
            except: self.alive = False

    def read_pty(self):
        while self.alive:
            try:
                d = self.pty.read(4096)
                if d: self.data_received.emit(d)
                else: break
            except: break

    def closeEvent(self, e):
        self.alive = False
        if self.pty: self.pty.terminate()
        super().closeEvent(e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EdithApp()
    window.show()
    sys.exit(app.exec())
