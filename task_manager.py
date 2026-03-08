from PyQt6.QtCore import QObject, pyqtSignal

class TaskManager(QObject):
    task_updated = pyqtSignal()
    plan_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.tasks = []
        self.implementation_plan = ""

    def add_task(self, title, status="todo"):
        self.tasks.append({"title": title, "status": status})
        self.task_updated.emit()

    def update_task(self, index, status):
        if 0 <= index < len(self.tasks):
            self.tasks[index]["status"] = status
            self.task_updated.emit()

    def set_plan(self, plan_markdown):
        self.implementation_plan = plan_markdown
        self.plan_updated.emit(plan_markdown)

    def clear_tasks(self):
        self.tasks = []
        self.task_updated.emit()
