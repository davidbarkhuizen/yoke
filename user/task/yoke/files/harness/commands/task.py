import uuid
from pathlib import Path

from harness.commands.abstract import AbstractHarnessCommand
from harness.task import load_prompt_request_for_task_from_disk, write_prompt_response_elements_to_disk
from harness.tether import prompt
from markdown.display import display_text_as_markdown
from markdown.render import dict_list_to_markdown_table
from model.model import RawPromptRequest, RawPromptResponse


class TaskCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "!"

    @property
    def usage(self) -> str:
        return f"{self.command} [task-name] [user-specification]"

    async def execute(self, model: str, args: list[str]) -> bool:

        if len(args) == 0:
            display_text_as_markdown(self.console, f"error, no task specified. usage is: {self.usage}")
            return False

        if len(args) == 1:
            display_text_as_markdown(self.console, f"error: **no user specification for task**. usage is: {self.usage}")
            return False

        task = args[0]
        user_specification_name = args[1]

        display_text_as_markdown(
            self.console,
            dict_list_to_markdown_table(
                [{"task": task, "model": model, "user task specification": user_specification_name}],
                alignment="left",
                column_order=["model", "task", "user task specification"],
            ),
        )

        user_prompt_root_folder_path: Path = Path(self.config.folders.user) / user_specification_name
        tasks_system_prompt_root_folder_path: Path = Path(self.config.folders.system)

        rq: RawPromptRequest = await load_prompt_request_for_task_from_disk(
            self.console, tasks_system_prompt_root_folder_path, user_prompt_root_folder_path, task
        )

        rsp: RawPromptResponse = await prompt(self.client, model, rq)

        task_outputs_folder: Path = user_prompt_root_folder_path / "generated" / str(uuid.uuid4())

        _ = await write_prompt_response_elements_to_disk(rsp, task_outputs_folder)
        return True
