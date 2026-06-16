import glob
from pathlib import Path

from harness.commands.abstract import AbstractHarnessCommand
from markdown.display import display_text_as_markdown


class ListTasksCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "list-tasks"

    async def execute(self, model: str, think: bool, args: list[str]) -> bool:

        root_task_specs_folder_path: Path = Path(self.config.folders.system) / "task"

        task_names: list[str] = [
            str(Path(spec_file_path).parent.relative_to(root_task_specs_folder_path))
            for spec_file_path in glob.glob(f"{root_task_specs_folder_path}/**/system.md", recursive=True)
        ]

        for task_name in task_names:
            print(task_name)

        return True
