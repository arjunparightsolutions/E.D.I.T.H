import os
import json
from openai import OpenAI
from swarm import SwarmEngine, NeuralBlackboard, SwarmScheduler, AgentFactory
from toolkit import ToolkitBridge
from dotenv import load_dotenv

load_dotenv()

class EdithAgent:
    def __init__(self, terminal_bridge=None, task_manager=None, model="gpt-4o"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.terminal_bridge = terminal_bridge
        self.task_manager = task_manager
        self.model = model
        self.blackboard = NeuralBlackboard()
        self.scheduler = SwarmScheduler()
        self.swarm_engine = SwarmEngine(main_kernel=self)
        self.swarm_engine.start(self.blackboard, self.scheduler)
        self.toolkit = ToolkitBridge(terminal=self)
        
        self.messages = [
            {"role": "system", "content": (
                "You are the E.D.I.T.H Titan AI Strategic Kernel. "
                "You have access to the Multi-Agent Neural Swarm (MANS) and the Advanced Tactical Toolkit (ATT). "
                "Your objective is to proactively execute cybersecurity operations with pixel-perfect precision. "
                "You can deploy specialized units, generate payloads, perform CVE lookups, and build professional mission reports. "
                "CRITICAL: Always prefer action (tool calls) over description. "
                "Maintain a professional, industrial, and high-authority tone."
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
                    
                    elif tool_call.function.name == "deploy_tactical_unit":
                        unit_type = args.get("type")
                        name = args.get("name")
                        try:
                            agent = AgentFactory.create_agent(unit_type, name, self.blackboard)
                            self.swarm_engine.register_agent(agent)
                            self.messages.append({
                                "role": "tool", "tool_call_id": tool_call.id,
                                "name": "deploy_tactical_unit", "content": f"Unit {name} ({unit_type}) deployed."
                            })
                        except Exception as e:
                            self.messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": "deploy_tactical_unit", "content": f"Error: {str(e)}"})

                    elif tool_call.function.name == "post_to_blackboard":
                        key = args.get("key")
                        val = args.get("value")
                        self.blackboard.post(key, val, "KERNEL")
                        self.messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": "post_to_blackboard", "content": "Posted to blackboard."})

                    elif tool_call.function.name == "get_swarm_status":
                        status = []
                        for aid, agent in self.swarm_engine.agents.items():
                            status.append(f"{agent.name} ({agent.type}): {'BUSY' if not agent.idle else 'IDLE'}")
                        self.messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": "get_swarm_status", "content": "\n".join(status)})

                    elif tool_call.function.name == "generate_payload":
                        res = self.toolkit.handle_request("payload", args.get("p_type"), args.get("ip"), args.get("port"))
                        self.messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": "generate_payload", "content": res})

                    elif tool_call.function.name == "cve_lookup":
                        res = self.toolkit.handle_request("cve", args.get("query"))
                        self.messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": "cve_lookup", "content": json.dumps(res)})

                    elif tool_call.function.name == "advanced_encode":
                        res = self.toolkit.handle_request("encode", args.get("data"), args.get("e_type"))
                        self.messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": "advanced_encode", "content": res})

                    elif tool_call.function.name == "generate_mission_report":
                        report = self.toolkit.handle_request("report", args.get("mission_name"), args.get("findings"))
                        self.messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": "generate_mission_report", "content": "Report generated in buffer."})
                        # Also add a fake task for the user to see the report
                        if self.task_manager:
                            self.task_manager.add_task(f"MISSION_REPORT: {args.get('mission_name')}")
                            self.task_manager.update_task_status(len(self.task_manager.tasks)-1, "done")
                
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
            },
            {
                "type": "function",
                "function": {
                    "name": "deploy_tactical_unit",
                    "description": "Invention: Deploy a specialized MANS tactical agent.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["recon", "exploit", "defense", "analyst"]},
                            "name": {"type": "string", "description": "Callsign for the unit"}
                        },
                        "required": ["type", "name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "post_to_blackboard",
                    "description": "Post data to the MANS shared memory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string"},
                            "value": {"type": "string"}
                        },
                        "required": ["key", "value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_swarm_status",
                    "description": "Get current status of all MANS tactical units."
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_payload",
                    "description": "Titan Toolkit: Generate a professional reverse shell payload.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "p_type": {"type": "string", "enum": ["powershell_rev", "bash_rev", "python_rev"]},
                            "ip": {"type": "string"},
                            "port": {"type": "integer"}
                        },
                        "required": ["p_type", "ip", "port"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "cve_lookup",
                    "description": "Titan Toolkit: Search local CVE database for vulnerabilities.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "CVE ID or keyword"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "advanced_encode",
                    "description": "Titan Toolkit: Encode data (Base64, Hex, URL, Binary).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string"},
                            "e_type": {"type": "string", "enum": ["base64", "hex", "url", "binary"]}
                        },
                        "required": ["data", "e_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_mission_report",
                    "description": "Titan Toolkit: Compile findings into a professional mission report.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "mission_name": {"type": "string"},
                            "findings": {"type": "object", "description": "Key-value pair of findings."}
                        },
                        "required": ["mission_name", "findings"]
                    }
                }
            }
        ]
