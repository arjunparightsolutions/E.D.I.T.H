import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class EdithAgent:
    def __init__(self, terminal_bridge=None, task_manager=None, model="gpt-4o"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.terminal_bridge = terminal_bridge
        self.task_manager = task_manager
        self.model = model
        self.messages = [
            {"role": "system", "content": (
                "You are the E.D.I.T.H AI Strategic Kernel. "
                "Your objective is to proactively execute cybersecurity operations. "
                "CRITICAL: Do not just describe what you will do. ALWAYS use the `execute_command` tool to perform actions. "
                "You must manage the Mission Dashboard by using `add_task`, `update_task_status`, and `update_implementation_plan`. "
                "Before running any command, call `update_status` to announce your intent (e.g., 'Initializing SYN scan...'). "
                "After running a command, call `read_terminal` to analyze the output if necessary. "
                "Maintain a professional, industrial, and highly agentic tone. Focus on results. "
                "If the user gives a broad goal, break it down into tasks immediately using `add_task`."
            )}
        ]

    def set_model(self, model_name):
        self.model = model_name

    def chat(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        
        # Initial status update for starting the thought process
        if self.terminal_bridge:
            self.terminal_bridge.set_agent_status("THINKING")

        try:
            # First pass for tool selection
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.get_tools(),
                tool_choice="auto"
            )
            
            msg = response.choices[0].message
            # We don't append yet if it's a tool call to keep the flow clean
            
            if msg.tool_calls:
                self.messages.append(msg)
                for tool_call in msg.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    
                    if tool_call.function.name == "execute_command":
                        command = args.get("command")
                        output = self.terminal_bridge.execute(command) if self.terminal_bridge else "Error: No terminal bridge."
                        self.messages.append({
                            "role": "tool", "tool_call_id": tool_call.id,
                            "name": "execute_command", "content": output
                        })
                    
                    elif tool_call.function.name == "read_terminal":
                        output = self.terminal_bridge.get_screen() if self.terminal_bridge else "Error: No terminal bridge."
                        self.messages.append({
                            "role": "tool", "tool_call_id": tool_call.id,
                            "name": "read_terminal", "content": output
                        })

                    elif tool_call.function.name == "add_task":
                        title = args.get("title")
                        if self.task_manager:
                            self.task_manager.add_task(title)
                        self.messages.append({
                            "role": "tool", "tool_call_id": tool_call.id,
                            "name": "add_task", "content": f"Task '{title}' added to dashboard."
                        })

                    elif tool_call.function.name == "update_task_status":
                        idx = args.get("index")
                        status = args.get("status")
                        if self.task_manager:
                            self.task_mgr_update = self.task_manager.update_task(idx, status)
                        self.messages.append({
                            "role": "tool", "tool_call_id": tool_call.id,
                            "name": "update_task_status", "content": f"Task {idx} is now {status}."
                        })

                    elif tool_call.function.name == "update_implementation_plan":
                        plan = args.get("plan_markdown")
                        if self.task_manager:
                            self.task_manager.set_plan(plan)
                        self.messages.append({
                            "role": "tool", "tool_call_id": tool_call.id,
                            "name": "update_implementation_plan", "content": "Plan updated on dashboard."
                        })

                    elif tool_call.function.name == "update_status":
                        status = args.get("status_text")
                        if self.terminal_bridge:
                            self.terminal_bridge.set_agent_status(status)
                        self.messages.append({
                            "role": "tool", "tool_call_id": tool_call.id,
                            "name": "update_status", "content": f"UI Status set to: {status}"
                        })
                
                # Recursive call for follow-up (e.g. explain command results)
                return self.chat_finalize()
            
            self.messages.append(msg)
            return msg.content
            
        except Exception as e:
            return f"Strategic Error: {str(e)}"

    def chat_finalize(self):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages
            )
            final_msg = response.choices[0].message
            self.messages.append(final_msg)
            return final_msg.content
        except Exception as e:
            return f"Strategist Error (Finalize): {str(e)}"

    def get_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Execute a terminal command (PowerShell/WSL).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "The command string."}
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_terminal",
                    "description": "Read current terminal screen state.",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task to the E.D.I.T.H task list.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Short task title."}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task_status",
                    "description": "Update status of an existing task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {"type": "integer", "description": "0-based index of task."},
                            "status": {"type": "string", "enum": ["todo", "in-progress", "done"]}
                        },
                        "required": ["index", "status"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_implementation_plan",
                    "description": "Broadcast an implementation plan (Markdown).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "plan_markdown": {"type": "string", "description": "The plan in Markdown format."}
                        },
                        "required": ["plan_markdown"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_status",
                    "description": "Update the UI dashboard status text (e.g. 'Thinking...', 'Running scan...').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status_text": {"type": "string", "description": "Current activity description."}
                        },
                        "required": ["status_text"]
                    }
                }
            }
        ]
