from harness.commands.abstract import AbstractHarnessCommand
from markdown.display import display_text_as_markdown


class SwitchThinkingModeCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "think"

    @property
    def usage(self) -> str:
        return f"{self.command} [true | false]"

    async def execute(self, model: str, think: bool, args: list[str]) -> bool:
        new_think: bool = bool(args[0])

        # TODO validate that thinking mode is supported by model

        updated: bool = self.update_setting("think", new_think)
        if not updated:
            display_text_as_markdown(self.console, "error: **failed to switch thinking mode**")
            return False

        display_text_as_markdown(self.console, f"thinking-mode switched to: {new_think}")
        return True
