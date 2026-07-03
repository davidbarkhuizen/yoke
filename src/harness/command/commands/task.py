from harness.command.abstract import AbstractHarnessCommand
from harness.task.task_logic import execute_task
from markdown.display import display_text_as_markdown
from model.model import RawPromptResponse


class TaskCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "!"

    @property
    def name(self) -> str:
        return "task"

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

        task: str = args[0]
        user_specification_name: str = args[1]

        rsp: RawPromptResponse | None = await execute_task(
            config=self.config,
            client=self.client,
            console=self.console,
            model=model,
            task=task,
            user_specification_name=user_specification_name,
        )
        return not rsp.failed if rsp is not None else False
