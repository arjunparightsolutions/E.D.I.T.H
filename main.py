import sys
import os
import threading
import time
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPlainTextEdit, QLabel, QPushButton, QHBoxLayout, 
                             QStackedWidget, QFrame, QMessageBox, QScrollArea, 
                             QLineEdit, QSplitter, QComboBox, QTextBrowser, 
                             QListWidget, QListWidgetItem, QSizePolicy, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QCoreApplication, QSize
from PyQt6.QtGui import QFont, QTextCursor, QKeyEvent, QColor, QIcon, QAction, QPainter
import qdarktheme
from winpty import PtyProcess
import pyte
from agent import EdithAgent
from task_manager import TaskManager
from dotenv import load_dotenv

load_dotenv()

# --- INDUSTRIAL DOCKER-STYLE DESIGN SYSTEM ---

STYLESHEET = """
QMainWindow {
    background-color: #121212;
}

#Sidebar {
    background-color: #1A1A1A;
    border-right: 1px solid #2A2A2A;
    min-width: 70px;
    max-width: 70px;
}

#TopToolbar {
    background-color: #1A1A1A;
    border-bottom: 1px solid #2A2A2A;
    min-height: 55px;
}

#DashboardCard {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 12px;
}

#DashboardTitle {
    color: #888888;
    font-weight: bold;
    font-size: 10px;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}

#StatusBadge {
    background-color: #2D2D2D;
    color: #00A3FF;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: bold;
    font-family: 'Segoe UI';
}

#ChatInput {
    background-color: #2D2D2D;
    color: #FFFFFF;
    border: 1px solid #444444;
    border-radius: 6px;
    padding: 12px;
    font-size: 13px;
    font-family: 'Segoe UI';
}

#ChatInput:focus {
    border: 1px solid #00A3FF;
}

#TerminalContainer {
    background-color: #000000;
    border: 1px solid #2A2A2A;
}

QScrollBar:vertical {
    border: none;
    background: #1A1A1A;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #333;
    min-height: 20px;
    border-radius: 4px;
}

QProgressBar {
    border: 1px solid #333;
    border-radius: 4px;
    text-align: center;
    color: transparent;
    background-color: #1A1A1A;
    height: 6px;
}

QProgressBar::chunk {
    background-color: #00A3FF;
}
"""

class SideNavButton(QPushButton):
    def __init__(self, icon_text, label, parent=None):
        super().__init__(parent)
        self.setFixedSize(70, 75)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(2)
        
        self.icon_lbl = QLabel(icon_text)
        self.icon_lbl.setStyleSheet("font-size: 20px; color: inherit; font-family: 'Consolas';")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.text_lbl = QLabel(label.upper())
        self.text_lbl.setStyleSheet("font-size: 8px; color: inherit; font-weight: bold; letter-spacing: 1px;")
        self.text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.text_lbl)
        
        self.setCheckable(True)
        self.update_style()
        self.toggled.connect(self.update_style)

    def update_style(self):
        if self.isChecked():
            self.setStyleSheet("background-color: #2D2D2D; color: #00A3FF; border-left: 3px solid #00A3FF; border-radius: 0;")
        else:
            self.setStyleSheet("background-color: transparent; color: #666666; border: none;")

class DashboardCard(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("DashboardCard")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        self.title_label = QLabel(title.upper())
        self.title_label.setObjectName("DashboardTitle")
        self.layout.addWidget(self.title_label)
        
        self.content_layout = QVBoxLayout()
        self.layout.addLayout(self.content_layout)
        self.layout.addStretch()

class TaskItem(QWidget):
    def __init__(self, title, status, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.icon = QLabel("○" if status == "todo" else "●" if status == "in-progress" else "✓")
        self.icon.setStyleSheet(f"color: {'#888' if status == 'todo' else '#00A3FF' if status == 'in-progress' else '#50FA7B'}; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.icon)
        
        self.label = QLabel(title)
        self.label.setStyleSheet(f"color: {'#DDD' if status != 'done' else '#666'}; font-size: 12px; font-family: 'Segoe UI';")
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
                    background-color: rgba(0, 163, 255, 0.04);
                    border-radius: 8px;
                    border-left: 2px solid #00A3FF;
                    margin-right: 40px;
                    padding: 10px;
                }
                QLabel { color: #BBB; font-size: 13px; font-family: 'Segoe UI'; }
            """)
        else:
            self.setStyleSheet("""
                ChatBubble {
                    background-color: #2D2D2D;
                    border-radius: 8px;
                    margin-left: 40px;
                    padding: 10px;
                    border: 1px solid #333;
                }
                QLabel { color: #FFF; font-size: 13px; font-family: 'Segoe UI'; }
            """)
        layout.addWidget(self.label)

# --- REFINED TERMINAL WIDGET ---

class TerminalWidget(QPlainTextEdit):
    key_pressed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)
        self.setFont(QFont("Consolas", 10))
        self.setStyleSheet("background-color: #050505; color: #00FF41; border: none; padding: 15px;")
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
            v_scroll = self.verticalScrollBar().value()
            self.setPlainText(full_text)
            self.last_text = full_text
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum() if v_scroll >= self.verticalScrollBar().maximum() - 20 else v_scroll)
        self.update_cursor_pos()

    def update_cursor_pos(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        for _ in range(self.screen.cursor.y): cursor.movePosition(QTextCursor.MoveOperation.Down)
        for _ in range(self.screen.cursor.x): cursor.movePosition(QTextCursor.MoveOperation.Right)
        self.setTextCursor(cursor)

# --- DOCKER-DESKTOP INSPIRED APP ---

class EdithApp(QMainWindow):
    data_received = pyqtSignal(str)
    ai_response_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("E.D.I.T.H Desktop - Tactical Cybersecurity Agent")
        self.resize(1650, 950)
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
        main_h_layout = QHBoxLayout(self.main_view)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)
        
        # --- 1. SIDE NAVIGATION ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.btn_dash = SideNavButton("📊", "Dash")
        self.btn_term = SideNavButton("⌨️", "Term")
        self.btn_sett = SideNavButton("⚙️", "Settings")
        self.btn_dash.setChecked(True)
        
        sidebar_layout.addWidget(self.btn_dash)
        sidebar_layout.addWidget(self.btn_term)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_sett)
        
        main_h_layout.addWidget(self.sidebar)
        
        # --- 2. WORKSPACE AREA ---
        workspace_v_layout = QVBoxLayout()
        workspace_v_layout.setContentsMargins(0, 0, 0, 0)
        workspace_v_layout.setSpacing(0)
        
        # Top Header
        self.header = QFrame()
        self.header.setObjectName("TopToolbar")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        logo = QLabel("E.D.I.T.H // AGENT_V1")
        logo.setStyleSheet("color: #FFFFFF; font-weight: 800; font-size: 15px; letter-spacing: 2px;")
        header_layout.addWidget(logo)
        
        header_layout.addStretch()
        
        self.auto_exec_btn = QPushButton("AUTO-EXEC: ON")
        self.auto_exec_btn.setCheckable(True)
        self.auto_exec_btn.setChecked(True)
        self.auto_exec_btn.setFixedWidth(130)
        self.auto_exec_btn.setStyleSheet("""
            QPushButton { background-color: #2D2D2D; color: #50FA7B; border: 1px solid #444; border-radius: 4px; font-weight: bold; font-size: 10px; padding: 5px; }
            QPushButton:checked { background-color: #1A3A1A; color: #50FA7B; border: 1px solid #50FA7B; }
            QPushButton:!checked { background-color: #3A1A1A; color: #FF5555; border: 1px solid #FF5555; }
        """)
        self.auto_exec_btn.toggled.connect(lambda c: self.auto_exec_btn.setText("AUTO-EXEC: ON" if c else "AUTO-EXEC: OFF"))
        header_layout.addWidget(self.auto_exec_btn)

        self.model_box = QComboBox()
        self.model_box.addItems(["gpt-4o", "gpt-4o-mini"])
        self.model_box.setFixedWidth(110)
        self.model_box.setStyleSheet("background-color: #2D2D2D; color: #BBB; border: 1px solid #444; padding: 3px; font-size: 11px;")
        header_layout.addWidget(QLabel("MODEL:", styleSheet="color: #666; font-size: 9px; margin-left: 15px;"))
        header_layout.addWidget(self.model_box)
        
        self.status_badge = QLabel("OFFLINE")
        self.status_badge.setObjectName("StatusBadge")
        header_layout.addWidget(self.status_badge)
        
        workspace_v_layout.addWidget(self.header)
        
        # Main Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("QSplitter::handle { background: #2A2A2A; }")
        
        # --- LEFT: MISSION CONTROL ---
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(15, 15, 8, 15)
        left_layout.setSpacing(15)
        
        # Dashboard Grid
        dash_row = QHBoxLayout()
        self.card_tasks = DashboardCard("Tactical Objectives")
        self.task_list_widget = QListWidget()
        self.task_list_widget.setStyleSheet("background: transparent; border: none;")
        self.card_tasks.content_layout.addWidget(self.task_list_widget)
        
        self.card_exec = DashboardCard("Command Intent")
        self.exec_label = QLabel("STANDBY_FOR_ORDERS")
        self.exec_label.setStyleSheet("color: #666; font-family: 'Consolas'; font-size: 11px; font-weight: bold;")
        self.exec_label.setWordWrap(True)
        self.card_exec.content_layout.addWidget(self.exec_label)
        
        dash_row.addWidget(self.card_tasks, stretch=3)
        dash_row.addWidget(self.card_exec, stretch=2)
        left_layout.addLayout(dash_row, stretch=1)
        
        # Strategic Chat
        chat_card = DashboardCard("Mission Strategist Thread")
        cv = QVBoxLayout()
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("background: transparent; border: none;")
        self.chat_inner = QWidget()
        self.chat_vbox = QVBoxLayout(self.chat_inner)
        self.chat_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_scroll.setWidget(self.chat_inner)
        cv.addWidget(self.chat_scroll)
        
        self.chat_input = QLineEdit()
        self.chat_input.setObjectName("ChatInput")
        self.chat_input.setPlaceholderText("Transmit tactical goal...")
        self.chat_input.returnPressed.connect(self.handle_chat)
        cv.addWidget(self.chat_input)
        
        chat_card.content_layout.addLayout(cv)
        left_layout.addWidget(chat_card, stretch=2)
        
        # --- RIGHT: TERMINAL & PLAN ---
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        right_layout.setContentsMargins(8, 15, 15, 15)
        right_layout.setSpacing(15)
        
        # Implementation Plan Header
        plan_card = DashboardCard("Session Deployment Strategy")
        plan_card.setFixedHeight(220)
        self.plan_view = QTextBrowser()
        self.plan_view.setStyleSheet("background: transparent; border: none; color: #AAA; font-size: 11px;")
        plan_card.content_layout.addWidget(self.plan_view)
        right_layout.addWidget(plan_card)
        
        # Interactive Terminal
        term_card = QFrame()
        term_card.setObjectName("TerminalContainer")
        term_l = QVBoxLayout(term_card)
        term_l.setContentsMargins(0, 0, 0, 0)
        
        term_hdr = QFrame()
        term_hdr.setFixedHeight(35)
        term_hdr.setStyleSheet("background-color: #1A1A1A; border-bottom: 1px solid #333;")
        tl = QHBoxLayout(term_hdr)
        tl.setContentsMargins(15, 0, 15, 0)
        tl.addWidget(QLabel("TACTICAL_TERMINAL_INTERFACE", styleSheet="color: #666; font-size: 10px; font-family: 'Consolas'; font-weight: bold;"))
        tl.addStretch()
        self.agent_status_lbl = QLabel("DISCONNECTED")
        self.agent_status_lbl.setStyleSheet("color: #00A3FF; font-size: 10px; font-weight: bold;")
        tl.addWidget(self.agent_status_lbl)
        term_l.addWidget(term_hdr)
        
        self.terminal = TerminalWidget()
        self.terminal.key_pressed.connect(self.send_to_pty)
        term_l.addWidget(self.terminal)
        
        right_layout.addWidget(term_card, stretch=1)

        self.splitter.addWidget(left_pane)
        self.splitter.addWidget(right_pane)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        
        workspace_v_layout.addWidget(self.splitter)
        main_h_layout.addLayout(workspace_v_layout)
        
        self.stack.addWidget(self.main_view)

    def setup_connections(self):
        self.data_received.connect(self.terminal.stream.feed)
        self.ai_response_ready.connect(self.post_ai_msg)
        self.task_mgr.task_updated.connect(self.sync_tasks)
        self.task_mgr.plan_updated.connect(self.plan_view.setMarkdown)

    def boot_system(self, shell):
        self.alive = True
        self.status_badge.setText(f"KERNEL: {shell.upper()}")
        self.status_badge.setStyleSheet("background-color: #00A3FF; color: black; font-weight: bold; border-radius: 4px; padding: 4px 10px;")
        self.agent_status_lbl.setText("READY")
        try:
            cmd = "powershell.exe" if shell == "powershell" else "wsl.exe"
            self.pty = PtyProcess.spawn(cmd, dimensions=(self.terminal.rows, self.terminal.cols))
            threading.Thread(target=self.read_pty, daemon=True).start()
            self.stack.setCurrentIndex(1)
            self.post_ai_msg("Agent initialized. Deep-bridge established. System is awaiting objective.")
        except Exception as e:
            QMessageBox.critical(self, "Kernel Crash", str(e))

    def handle_chat(self):
        txt = self.chat_input.text().strip()
        if not txt: return
        self.chat_input.clear()
        self.add_bubble(txt, False)
        self.set_agent_status("THINKING")
        threading.Thread(target=lambda: self.ai_response_ready.emit(self.agent.chat(txt)), daemon=True).start()

    def post_ai_msg(self, text):
        self.set_agent_status("READY")
        self.add_bubble(text, True)

    def set_agent_status(self, text):
        self.agent_status_lbl.setText(text.upper())

    def add_bubble(self, text, is_ai):
        self.chat_vbox.addWidget(ChatBubble(text, is_ai))
        QCoreApplication.processEvents()
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())

    def sync_tasks(self):
        self.task_list_widget.clear()
        for t in self.task_mgr.tasks:
            item = QListWidgetItem()
            widget = TaskItem(t['title'], t['status'])
            item.setSizeHint(widget.sizeHint())
            self.task_list_widget.addItem(item)
            self.task_list_widget.setItemWidget(item, widget)

    def execute(self, cmd):
        self.set_agent_status("EXECUTING")
        self.exec_label.setText(f"> {cmd}")
        self.exec_label.setStyleSheet("color: #00A3FF; font-family: 'Consolas'; font-size: 11px; font-weight: bold;")
        
        if self.auto_exec_btn.isChecked():
            self.send_to_pty(cmd + "\r\n")
            time.sleep(1.8) # Wait for initial output
            self.set_agent_status("ANALYZING")
            return self.get_screen() # Return actual terminal content
        else:
            self.set_agent_status("AWAITING_AUTH")
            return "AUTO-EXEC DISABLED. USER AUTH REQUIRED."

    def get_screen(self): 
        # Extract meaningful text from the screen buffer
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
