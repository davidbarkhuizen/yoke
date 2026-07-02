import glob
from pathlib import Path

from harness.command.abstract import AbstractHarnessCommand
from markdown.display import display_text_as_markdown
from markdown.render import dict_list_to_markdown_table


class ListTasksCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "list-tasks"

    async def execute(self, model: str, args: list[str]) -> bool:

        root_task_specs_folder_path: Path = Path(self.config.folders.system) / "task"

        task_names: list[str] = [
            str(Path(spec_file_path).parent.relative_to(root_task_specs_folder_path))
            for spec_file_path in glob.glob(f"{root_task_specs_folder_path}/**/system.md", recursive=True)
        ]

        display_text_as_markdown(
            self.console,
            dict_list_to_markdown_table([{"task": task} for task in sorted(task_names)], alignment="right"),
        )

        return True
