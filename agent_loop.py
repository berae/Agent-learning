import json
from openai import OpenAI
from tools import list_dir, read_file, run_shell


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

MODEL_NAME = "qwen2.5:7b-instruct-q4_K_M"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files and folders in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path, default is current directory"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file and return its content",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the text file"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a safe shell command in Windows PowerShell/cmd environment",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Safe command such as dir, type, echo, findstr"
                    }
                },
                "required": ["command"]
            }
        }
    }
]


def call_tool(name: str, args: dict) -> str:
    if name == "list_dir":
        return list_dir(args.get("path", "."))
    if name == "read_file":
        return read_file(args["path"])
    if name == "run_shell":
        return run_shell(args["command"])
    return "error: unknown tool"


def run_agent(user_input: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a local file assistant running on the user's computer. "
                "You can use tools to inspect directories, read files, and run safe shell commands. "
                "When a task needs file system information, use tools instead of guessing. "
                "Answer clearly and briefly."
            )
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    for _ in range(6):
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS
        )

        msg = response.choices[0].message

        if getattr(msg, "tool_calls", None):
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in msg.tool_calls
                ]
            })

            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments or "{}")
                tool_result = call_tool(tc.function.name, args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_result
                })
        else:
            return msg.content or "(no content)"

    return "Reached tool-call limit."