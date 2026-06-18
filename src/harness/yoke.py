import traceback
from typing import Sequence

from ollama import AsyncClient
from rich.console import Console

from config import YokeConfig
from harness.commands.abstract import AbstractHarnessCommand
from harness.commands.help import HelpCommand
from harness.commands.invoke import InvokeCommand
from harness.commands.list_commands import ListCommandsCommand
from harness.commands.list_models import ListModelsCommand
from harness.commands.list_tasks import ListTasksCommand
from harness.commands.ps import PSCommand
from harness.commands.task import TaskCommand
from harness.tether import new_async_ollama_client
from markdown.display import display_text_as_markdown, new_markdown_console


async def execute_harness_command(console, model: str, command: AbstractHarnessCommand, args: list[str]) -> bool:

    succeeded: bool = False
    try:
        succeeded = await command.execute(model, args)
    except Exception as e:
        stack_trace: str = "\n".join(traceback.format_exception(e))
        error_message: str = f"error: unhandled exception during harness command execution - {e} - {stack_trace}"
        display_text_as_markdown(console, error_message)

    return succeeded


async def harness_llm(client: AsyncClient, config: YokeConfig):
    console: Console = new_markdown_console()
    model = config.ollama.default_model

    harness_commands: Sequence[AbstractHarnessCommand] = list()
    harness_commands.extend(
        [
            T_HarnessCommand(config, client, console, harness_commands)
            for T_HarnessCommand in [
                ListModelsCommand,
                InvokeCommand,
                TaskCommand,
                PSCommand,
                ListCommandsCommand,
                HelpCommand,
                ListTasksCommand,
            ]
        ]
    )

    def match_harness_command(command_name: str) -> AbstractHarnessCommand | None:
        matching_commands = [cmd for cmd in harness_commands if cmd.command == command_name]
        if len(matching_commands) == 0:
            display_text_as_markdown(console, f"error:  **unknown harness command: {command_name}**")
            return None

        if len(matching_commands) > 1:
            display_text_as_markdown(
                console,
                f"error:  **invalid harness command configuration, multiple commands found matching {command_name}**",
            )
            return None

        return matching_commands[0]

    help_command: AbstractHarnessCommand | None = match_harness_command("help")
    if help_command is None:
        raise ValueError("cannot locate help command")

    await execute_harness_command(console, model, help_command, [])

    while (invocation := input(f"\n{model} > ").strip().lower()) not in ["exit", "quit"]:
        if len(invocation) == 0:
            continue

        splut: list[str] = list()
        try:
            splut = invocation.split(" ")
        except Exception as e:
            display_text_as_markdown(console, f"error: exception parsing harness command {invocation}: {e}")
            continue

        match splut:
            case []:
                continue
            case [command_name, *command_args]:
                command: AbstractHarnessCommand | None = match_harness_command(command_name)
                if command is None:
                    continue
                await execute_harness_command(console, model, command, command_args)


async def yoke(config: YokeConfig):
    client = new_async_ollama_client(config.ollama.host, config.ollama.port)
    try:
        await harness_llm(client, config)
    except:
        traceback.print_exc()
        raise
    finally:
        await client.close()
