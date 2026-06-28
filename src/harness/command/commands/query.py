from harness.command.abstract import AbstractHarnessCommand
from harness.tether import prompt_and_handle_tool_calls
from harness.tool.tool_registry import load_tools
from model.model import RawPromptRequest, Tool


class QueryCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "?"

    @property
    def name(self) -> str:
        return "natural language query"

    @property
    def usage(self) -> str:
        return "? [natural language query]"

    async def execute(self, model: str, args: list[str]) -> bool:

        text = " ".join(args)

        available_tools: list[Tool] = [tool for tool in load_tools()]

        rq = RawPromptRequest(system_prompt="", user_prompt=[text], tools=available_tools)
        rsp = await prompt_and_handle_tool_calls(self.console, self.client, model, rq, available_tools)

        return not rsp.failed
