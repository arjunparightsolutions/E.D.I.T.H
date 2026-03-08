# Swarm Plugin Extensibility System
import importlib.util

class SwarmPluginSystem:
    @staticmethod
    def load_custom_agent(plugin_path, class_name):
        spec = importlib.util.spec_from_file_location(class_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, class_name)
