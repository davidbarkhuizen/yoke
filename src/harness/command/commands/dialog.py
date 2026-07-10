from datetime import datetime
from pathlib import Path
from typing import Any

from harness.command.abstract import AbstractHarnessCommand
from harness.task.task_logic import write_prompt_response_elements_to_disk
from harness.tether import prompt_and_handle_tool_calls
from harness.tool.tool_registry import load_tools
from model.model import RawPromptRequest, Tool


class DialogCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "dialog"

    @property
    def name(self) -> str:
        return "natural language dialogue"

    async def execute(self, model: str, args: list[str]) -> bool:
        available_tools: list[Tool] = load_tools()
        available_tools.clear()

        message_history: list[dict[str, Any]] = []

        print("enter '!exit' to end dialogue")
        print("enter '!new' to start a new dialogue")
        while True:
            utterance: str = input("> ").strip()
            if len(utterance) == 0:
                continue
            if utterance.lower() == "!exit":
                break
            if utterance.lower() == "!new":
                message_history.clear()
                continue

            rq = RawPromptRequest(
                system_prompt="", user_prompts=[utterance], tools=available_tools, message_history=message_history
            )
            rsp = await prompt_and_handle_tool_calls(self.console, self.client, model, rq, available_tools)

            now: datetime = datetime.now()
            query_outputs_folder: Path = (
                Path(self.config.folders.user) / "query" / now.strftime("%Y%m%d") / now.strftime("%H%M_%S")
            )

            _ = await write_prompt_response_elements_to_disk(self.console, rsp, query_outputs_folder)

            message_history.clear()
            message_history.extend(rsp.message_history)

        return True
