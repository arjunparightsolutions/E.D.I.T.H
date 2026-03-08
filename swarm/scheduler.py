import queue

class SwarmScheduler:
    def __init__(self):
        self.task_queue = queue.PriorityQueue()

    def add_task(self, task_priority, task_data):
        # task_data should include 'target_type', 'command', etc.
        self.task_queue.put((task_priority, task_data))
        print(f"[SCHEDULER] Task Added: Priority {task_priority}")

    def get_next_task(self):
        try:
            priority, task = self.task_queue.get_nowait()
            return task
        except queue.Empty:
            return None

    def is_empty(self):
        return self.task_queue.empty()
