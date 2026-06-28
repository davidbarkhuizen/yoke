import glob
import importlib
import os
from pathlib import Path

from model.model import Tool, ToolTag


def load_tools() -> list[Tool]:

    script_dir = Path(__file__).resolve().parent
    tools_root_folder = script_dir / "tools"

    root_folder: str = str(tools_root_folder.absolute())
    tool_file_module_paths: list[str] = [
        f.replace(root_folder, "").replace("/", ".").replace(".py", "")
        for f in glob.glob(os.path.join(root_folder, "**", "tool.py"), recursive=True)
    ]

    module_root: str = "harness.tool.tools"
    return [importlib.import_module(f"{module_root}{module_path}").new_tool() for module_path in tool_file_module_paths]


def tools_for_tag(tools: list[Tool], tag: ToolTag) -> list[Tool]:
    return [tool for tool in tools if tag in tool.tags]
