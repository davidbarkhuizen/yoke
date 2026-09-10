import glob
import importlib
import os
from pathlib import Path

from model.model import Tool, ToolTag


def load_tools(tags: list[ToolTag] | None = None) -> list[Tool]:

    script_dir = Path(__file__).resolve().parent
    tools_root_folder = script_dir / "tools"

    root_folder: str = str(tools_root_folder.absolute())
    tool_file_module_paths: list[str] = [
        f.replace(root_folder, "").replace("/", ".").replace(".py", "")
        for f in glob.glob(os.path.join(root_folder, "**", "tool.py"), recursive=True)
    ]

    module_root: str = "harness.tool.tools"
    all_tools = [
        importlib.import_module(f"{module_root}{module_path}").new_tool() for module_path in tool_file_module_paths
    ]

    if not tags:
        return all_tools

    return [tool for tool in all_tools if any(tag in tags for tag in tool.tags)]


def tools_for_tag(tools: list[Tool], tag: ToolTag) -> list[Tool]:
    return [tool for tool in tools if tag in tool.tags]
