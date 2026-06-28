from typing import Any, Callable, Mapping

from ollama import Message

from markdown.display import display_text_as_markdown
from markdown.render import dict_list_to_markdown_table
from model.model import Tool


async def call_tool(console, tools: list[Tool], tool_call: Message.ToolCall) -> str:

    target_tool_name: str = tool_call.function.name
    tool_call_arguments: Mapping[str, Any] = tool_call.function.arguments

    display_text_as_markdown(console, f"tool: **{target_tool_name}**")
    if len(tool_call_arguments.keys()) > 0:
        display_text_as_markdown(console, "**Arguments**")
        display_text_as_markdown(console, dict_list_to_markdown_table([tool_call_arguments]))

    matching_tool_fns = [tool.function for tool in tools if tool.name == target_tool_name]
    if len(matching_tool_fns) == 0:
        error: str = (
            f"cannot find a tool matching {target_tool_name}. available: {', '.join([tool.name for tool in tools])}"
        )
        display_text_as_markdown(console, f"**{error}**")

    tool_fn: Callable = matching_tool_fns[0]
    tool_call_result: str = await tool_fn(**tool_call_arguments)

    display_text_as_markdown(console, f"result: {tool_call_result}")

    return tool_call_result
