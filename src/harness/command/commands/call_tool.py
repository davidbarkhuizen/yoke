from datetime import datetime
from pathlib import Path

from ollama import Message

from harness.command.abstract import AbstractHarnessCommand
from harness.task.task_logic import write_prompt_response_elements_to_disk
from harness.tether import prompt_and_handle_tool_calls
from harness.tool.tool_logic import call_tool
from harness.tool.tool_registry import load_tools
from model.model import RawPromptRequest, Tool


class CallToolCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "call-tool"

    @property
    def name(self) -> str:
        return "call-tool"

    @property
    def usage(self) -> str:
        return "call-tool [tool-name] [arguments-map]"

    async def execute(self, model: str, args: list[str]) -> bool:

        tools: list[Tool] = [tool for tool in load_tools()]

        tool_name = args[0]

        tool_args_components = args[1:]
        arguments_str = " ".join(tool_args_components)

        msg_tool_call = Message.ToolCall(
            function=Message.ToolCall.Function(name=tool_name, arguments=eval(arguments_str))
        )

        try:
            tool_call_response: str | None = await call_tool(self.console, tools, msg_tool_call)
            print(tool_call_response)
        except Exception:
            return False

        return True
