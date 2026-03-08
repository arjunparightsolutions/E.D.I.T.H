import sys
import os
import threading
import time
import json
import math
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPlainTextEdit, QLabel, QPushButton, QHBoxLayout, 
                             QStackedWidget, QFrame, QMessageBox, QScrollArea, 
                             QLineEdit, QSplitter, QComboBox, QTextBrowser, 
                             QListWidget, QListWidgetItem, QSizePolicy, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QCoreApplication, QSize, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PyQt6.QtGui import QFont, QTextCursor, QKeyEvent, QColor, QIcon, QAction, QPainter, QLinearGradient, QBrush, QPen, QRadialGradient
import qdarktheme
from winpty import PtyProcess
import pyte
from agent import EdithAgent
from task_manager import TaskManager
from dotenv import load_dotenv

load_dotenv()

# --- ZENITH PROFESSIONAL DESIGN SYSTEM (24px Grid + Glow) ---

STYLESHEET = """
QMainWindow {
    background-color: #060607;
}

#Sidebar {
    background-color: #09090B;
    border-right: 1px solid #15151A;
    min-width: 90px;
    max-width: 90px;
}

#TopToolbar {
    background-color: #09090B;
    border-bottom: 1px solid #15151A;
    min-height: 80px;
}

#DashboardCard {
    background-color: rgba(15, 15, 18, 0.7);
    border: 1px solid rgba(0, 163, 255, 0.1);
    border-radius: 18px;
}

#DashboardCard:hover {
    border: 1px solid rgba(0, 163, 255, 0.3);
    background-color: rgba(20, 20, 25, 0.8);
}

#DashboardTitle {
    color: #3A3A40;
    font-weight: 900;
    font-size: 9px;
    letter-spacing: 4px;
    margin-bottom: 15px;
}

#StatusBadge {
    background-color: rgba(0, 255, 65, 0.03);
    color: #00FF41;
    padding: 10px 20px;
    border: 1px solid rgba(0, 255, 65, 0.15);
    border-radius: 10px;
    font-size: 10px;
    font-weight: 900;
    font-family: 'JetBrains Mono';
    letter-spacing: 1px;
}

#ChatInput {
    background-color: #0F0F12;
    color: #FFFFFF;
    border: 1px solid #1A1A1E;
    border-radius: 14px;
    padding: 18px;
    font-size: 14px;
    font-family: 'Inter', sans-serif;
}

#ChatInput:focus {
    border: 1px solid #00A3FF;
    background-color: #121215;
}

#TerminalContainer {
    background-color: #020203;
    border: 1px solid #15151A;
    border-radius: 20px;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 3px;
}

QScrollBar::handle:vertical {
    background: #15151A;
    min-height: 50px;
    border-radius: 1px;
}
"""

class GlassCard(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("DashboardCard")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        
        self.title_label = QLabel(title.upper())
        self.title_label.setObjectName("DashboardTitle")
        self.layout.addWidget(self.title_label)
        
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        self.layout.addLayout(self.content_layout)
        self.layout.addStretch()

# --- ZENITH VISUAL ANALYTICS ---

class NeuralHeatmap(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.points = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_heat)
        self.timer.start(100)

    def update_heat(self):
        if len(self.points) > 50: self.points.pop(0)
        self.points.append(random.randint(20, 80))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        step = w / 50
        
        path = QPen(QColor("#00A3FF"), 2)
        painter.setPen(path)
        
        for i in range(len(self.points) - 1):
            x1, y1 = i * step, h - (self.points[i] * h / 100)
            x2, y2 = (i+1) * step, h - (self.points[i+1] * h / 100)
            painter.drawLine(QPoint(int(x1), int(y1)), QPoint(int(x2), int(y2)))
            
            # Glow effect
            g_pen = QPen(QColor(0, 163, 255, 30), 6)
            painter.setPen(g_pen)
            painter.drawLine(QPoint(int(x1), int(y1)), QPoint(int(x2), int(y2)))
            painter.setPen(path)

class KernelStream(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.offset = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def animate(self):
        self.offset += 0.1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        mid_y = h / 2
        
        painter.setPen(QPen(QColor("#00FF41"), 1))
        
        for x in range(0, w, 2):
            y = mid_y + math.sin(x * 0.05 + self.offset) * 15
            painter.drawPoint(x, int(y))

class SideNavButton(QPushButton):
    def __init__(self, icon_text, label, parent=None):
        super().__init__(parent)
        self.setFixedSize(90, 100)
        self.setCheckable(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(8)
        
        self.icon_lbl = QLabel(icon_text)
        self.icon_lbl.setStyleSheet("font-size: 26px; color: inherit;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.text_lbl = QLabel(label.upper())
        self.text_lbl.setStyleSheet("font-size: 9px; color: inherit; font-weight: 900; letter-spacing: 3px;")
        self.text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.text_lbl)
        
        self.update_style()
        self.toggled.connect(self.update_style)

    def update_style(self):
        if self.isChecked():
            self.setStyleSheet("background-color: #0F0F12; color: #00A3FF; border-right: 4px solid #00A3FF;")
        else:
            self.setStyleSheet("background-color: transparent; color: #2A2A30; border: none;")

class PulseIndicator(QWidget):
    def __init__(self, color="#00A3FF", parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.color = QColor(color)
        self.alpha = 255
        self.growing = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pulse)
        self.timer.start(40)

    def update_pulse(self):
        if self.growing:
            self.alpha += 8
            if self.alpha >= 255: self.growing = False
        else:
            self.alpha -= 8
            if self.alpha <= 40: self.growing = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QColor(self.color)
        c.setAlpha(self.alpha)
        painter.setBrush(QBrush(c))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 8, 8)

class TaskItem(QWidget):
    def __init__(self, title, status, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        
        dot = PulseIndicator("#00A3FF" if status == "in-progress" else "#00FF41" if status == "done" else "#15151A")
        layout.addWidget(dot)
        
        self.label = QLabel(title)
        self.label.setStyleSheet(f"color: {'#DDD' if status != 'done' else '#333'}; font-size: 13px; font-weight: 700; font-family: 'Inter';")
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
                    background-color: rgba(0, 163, 255, 0.02);
                    border-radius: 20px;
                    border: 1px solid rgba(0, 163, 255, 0.05);
                    margin-right: 100px;
                    padding: 24px;
                }
                QLabel { color: #999; font-size: 14px; line-height: 1.7; font-family: 'Inter'; }
            """)
        else:
            self.setStyleSheet("""
                ChatBubble {
                    background-color: #0F0F12;
                    border-radius: 20px;
                    margin-left: 100px;
                    padding: 24px;
                    border: 1px solid #1A1A1E;
                }
                QLabel { color: #FFFFFF; font-size: 14px; font-family: 'Inter'; }
            """)
        layout.addWidget(self.label)

# --- ZENITH TERMINAL WIDGET ---

class TerminalWidget(QPlainTextEdit):
    key_pressed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)
        self.setFont(QFont("JetBrains Mono", 10))
        self.setStyleSheet("background-color: #020203; color: #00FF41; border: none; padding: 30px;")
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

# --- ZENITH MAIN KERNEL ---

class EdithApp(QMainWindow):
    data_received = pyqtSignal(str)
    ai_response_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("E.D.I.T.H Zenith - Tactical OS")
        self.resize(1850, 1150)
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
        
        # --- 1. ZENITH SIDE NAV ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.btn_dash = SideNavButton("📊", "Dash")
        self.btn_term = SideNavButton("⌨️", "Term")
        self.btn_toolkit = SideNavButton("🛠️", "ATT")
        self.btn_dash.setChecked(True)
        
        sidebar_layout.addWidget(self.btn_dash)
        sidebar_layout.addWidget(self.btn_term)
        sidebar_layout.addWidget(self.btn_toolkit)
        sidebar_layout.addStretch()
        
        # Kernel Status Footer (Pulse Indicator)
        kernel_footer = QVBoxLayout()
        kernel_footer.setContentsMargins(0, 0, 0, 40)
        kernel_footer.setSpacing(10)
        self.pulse = PulseIndicator("#15151A")
        kernel_footer.addWidget(self.pulse, alignment=Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel("ZENITH_V2.5")
        lbl.setStyleSheet("font-size: 9px; color: #222; font-weight: 900; letter-spacing: 3px;")
        kernel_footer.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addLayout(kernel_footer)
        
        main_layout.addWidget(self.sidebar)
        
        # --- 2. CORE WORKSPACE ---
        workspace = QVBoxLayout()
        workspace.setContentsMargins(0, 0, 0, 0)
        workspace.setSpacing(0)
        
        # Zenith Header
        header = QFrame()
        header.setObjectName("TopToolbar")
        header_l = QHBoxLayout(header)
        header_l.setContentsMargins(40, 0, 40, 0)
        
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        title_box.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        logo = QLabel("E.D.I.T.H // ZENITH_TACTICAL")
        logo.setStyleSheet("color: #FFFFFF; font-weight: 950; font-size: 20px; letter-spacing: 6px;")
        sub_logo = QLabel("ULTIMATE AGENTIC HUB // NEURAL_GRID_v2.5")
        sub_logo.setStyleSheet("color: #00A3FF; font-weight: 900; font-size: 9px; letter-spacing: 6px;")
        title_box.addWidget(logo)
        title_box.addWidget(sub_logo)
        header_l.addLayout(title_box)
        
        header_l.addStretch()
        
        self.status_badge = QLabel("OFFLINE")
        self.status_badge.setObjectName("StatusBadge")
        header_l.addWidget(self.status_badge)
        
        workspace.addWidget(header)
        
        # Primary Workspace Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("QSplitter::handle { background: #15151A; }")
        
        # --- LEFT: MISSION & STRATEGY ---
        left_pane = QWidget()
        left_pane_l = QVBoxLayout(left_pane)
        left_pane_l.setContentsMargins(40, 40, 20, 40)
        left_pane_l.setSpacing(30)
        
        # Top Row Dash (Analytics + Tasks)
        dash_grid = QHBoxLayout()
        dash_grid.setSpacing(24)
        
        self.card_tasks = GlassCard("Tactical Objectives")
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("background: transparent; border: none;")
        self.card_tasks.content_layout.addWidget(self.task_list)
        
        self.card_neural = GlassCard("Neural Activity Heatmap")
        self.heatmap = NeuralHeatmap()
        self.card_neural.content_layout.addWidget(self.heatmap)
        
        self.card_swarm = GlassCard("Swarm Hub")
        self.swarm_list = QListWidget()
        self.swarm_list.setStyleSheet("background: transparent; border: none;")
        self.card_swarm.content_layout.addWidget(self.swarm_list)
        
        dash_grid.addWidget(self.card_tasks, stretch=2)
        dash_grid.addWidget(self.card_neural, stretch=3)
        dash_grid.addWidget(self.card_swarm, stretch=2)
        left_pane_l.addLayout(dash_grid, stretch=2)
        
        # AI Strategist Thread
        chat_card = GlassCard("Zenith Neural Bridge")
        cv = QVBoxLayout()
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("background: transparent; border: none;")
        self.chat_inner = QWidget()
        self.chat_vbox = QVBoxLayout(self.chat_inner)
        self.chat_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_inner.setStyleSheet("background: transparent;")
        self.chat_scroll.setWidget(self.log_widget if hasattr(self, 'log_widget') else self.chat_inner) # Wait, fix this
        self.chat_scroll.setWidget(self.chat_inner)
        cv.addWidget(self.chat_scroll)
        
        self.chat_input = QLineEdit()
        self.chat_input.setObjectName("ChatInput")
        self.chat_input.setPlaceholderText("Transmit Zenith directive...")
        self.chat_input.returnPressed.connect(self.handle_chat)
        cv.addWidget(self.chat_input)
        
        chat_card.content_layout.addLayout(cv)
        left_pane_l.addWidget(chat_card, stretch=5)
        
        # --- RIGHT: DEPLOYMENT & LOGS ---
        right_pane = QWidget()
        right_pane_l = QVBoxLayout(right_pane)
        right_pane_l.setContentsMargins(20, 40, 40, 40)
        right_pane_l.setSpacing(30)
        
        # Command HUD + Visual Stream
        hud_card = GlassCard("Tactical Hud")
        hud_card.setFixedHeight(280)
        hl = QVBoxLayout()
        self.exec_preview = QLabel("NO_ACTIVE_INTENT")
        self.exec_preview.setStyleSheet("color: #444; font-family: 'JetBrains Mono'; font-size: 11px; font-weight: 900;")
        self.exec_preview.setWordWrap(True)
        hl.addWidget(self.exec_preview)
        hl.addStretch()
        self.stream_viz = KernelStream()
        hl.addWidget(self.stream_viz)
        hud_card.content_layout.addLayout(hl)
        right_pane_l.addWidget(hud_card)
        
        # Terminal Pane
        term_frame = QFrame()
        term_frame.setObjectName("TerminalContainer")
        term_layout = QVBoxLayout(term_frame)
        term_layout.setContentsMargins(0, 0, 0, 0)
        
        term_header = QFrame()
        term_header.setFixedHeight(60)
        term_header.setStyleSheet("background-color: #09090B; border-bottom: 1px solid #15151A;")
        tl = QHBoxLayout(term_header)
        tl.setContentsMargins(30, 0, 30, 0)
        tl.addWidget(QLabel("⌨️ ZENITH_CORE_PTY", styleSheet="color: #444; font-size: 11px; font-weight: 900; letter-spacing: 3px;"))
        tl.addStretch()
        self.agent_status = QLabel("IDLE")
        self.agent_status.setStyleSheet("color: #00FF41; font-size: 10px; font-weight: 900; background: rgba(0, 255, 65, 0.03); padding: 6px 15px; border-radius: 8px;")
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
        
        # --- QUICK-ACTION HUD ---
        quick_bar = QFrame()
        quick_bar.setFixedHeight(60)
        quick_bar.setStyleSheet("background-color: #0B0B0D; border-top: 1px solid #15151A;")
        ql = QHBoxLayout(quick_bar)
        ql.setContentsMargins(40, 0, 40, 0)
        ql.setSpacing(20)
        
        actions = [("🔍 RECON_SWARM", "Deploy a recon swarm"), ("💀 EXPLOIT_SWARM", "Deploy an exploit swarm"), ("🛠️ GEN_PAYLOAD", "Generate a reverse shell payload"), ("📄 GEN_REPORT", "Generate a mission report")]
        for label, cmd in actions:
            btn = QPushButton(label)
            btn.setStyleSheet("""
                QPushButton { background: rgba(0, 163, 255, 0.05); color: #00A3FF; border: 1px solid rgba(0, 163, 255, 0.1); border-radius: 8px; font-weight: 900; font-size: 10px; padding: 0 15px; height: 32px; }
                QPushButton:hover { background: #00A3FF; color: black; }
            """)
            btn.clicked.connect(lambda checked, c=cmd: self.send_to_chat(c))
            ql.addWidget(btn)
        ql.addStretch()
        workspace.addWidget(quick_bar)
        
        main_layout.addLayout(workspace)
        self.stack.addWidget(self.main_view)

    def setup_connections(self):
        self.data_received.connect(self.terminal.stream.feed)
        self.ai_response_ready.connect(self.post_ai_msg)
        self.task_mgr.task_updated.connect(self.sync_tasks)
        
        self.swarm_timer = QTimer(self)
        self.swarm_timer.timeout.connect(self.sync_swarm)
        self.swarm_timer.start(1000)

    def boot_system(self, shell):
        self.alive = True
        self.status_badge.setText(f"ZENITH_KERNAL: {shell.upper()}")
        self.status_badge.setStyleSheet("background-color: rgba(0, 255, 65, 0.08); color: #00FF41; border: 1px solid rgba(0, 255, 65, 0.3);")
        self.pulse.color = QColor("#00FF41")
        try:
            cmd = "powershell.exe" if shell == "powershell" else "wsl.exe"
            self.pty = PtyProcess.spawn(cmd, dimensions=(self.terminal.rows, self.terminal.cols))
            threading.Thread(target=self.read_pty, daemon=True).start()
            self.stack.setCurrentIndex(1)
            self.post_ai_msg("Zenith Neural Kernel synchronized. All Tactical Swarms and Toolkit modules active. Transmit directive.")
        except Exception as e:
            QMessageBox.critical(self, "Boot Failure", str(e))

    def handle_chat(self):
        txt = self.chat_input.text().strip()
        if not txt: return
        self.chat_input.clear()
        self.add_bubble(txt, False)
        self.set_agent_status("STRATEGIZING")
        threading.Thread(target=lambda: self.ai_response_ready.emit(self.agent.chat(txt)), daemon=True).start()

    def send_to_chat(self, txt):
        self.chat_input.setText(txt)
        self.handle_chat()

    def post_ai_msg(self, text):
        self.set_agent_status("READY")
        self.add_bubble(text, True)

    def set_agent_status(self, text):
        self.agent_status.setText(text.upper())
        self.pulse.color = QColor("#00A3FF" if text == "READY" else "#00FF41" if "EXEC" in text else "#FFDD00")

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
            status_text = f"[{agent.type.upper()}] {agent.name}"
            item = QListWidgetItem()
            widget = TaskItem(status_text, "in-progress" if not agent.idle else "todo")
            item.setSizeHint(widget.sizeHint())
            self.swarm_list.addItem(item)
            self.swarm_list.setItemWidget(item, widget)

    def execute(self, cmd):
        self.set_agent_status("EXECUTING")
        self.exec_preview.setText(f"> {cmd}")
        self.exec_preview.setStyleSheet("color: #00FF41; font-family: 'JetBrains Mono'; font-size: 11px; font-weight: 900;")
        self.send_to_pty(cmd + "\r\n")
        time.sleep(1.5)
        return self.get_screen()

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
