import threading

class NeuralBlackboard:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()
        self.observers = []

    def post(self, key, value, source_agent="system"):
        with self.lock:
            self.data[key] = {
                "value": value,
                "source": source_agent,
                "timestamp": threading.current_thread().name # Placeholder for time
            }
            print(f"[BLACKBOARD] Update: {key} by {source_agent}")
        self.notify_observers(key, value)

    def get(self, key):
        with self.lock:
            return self.data.get(key, {}).get("value")

    def subscribe(self, callback):
        self.observers.append(callback)

    def notify_observers(self, key, value):
        for observer in self.observers:
            try:
                observer(key, value)
            except:
                pass

    def get_all(self):
        with self.lock:
            return self.data.copy()
