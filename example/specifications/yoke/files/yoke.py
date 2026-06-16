import traceback
from typing import Any, Sequence

from ollama import AsyncClient
from rich.console import Console

from config import YokeConfig
from harness.commands.abstract import AbstractHarnessCommand
from harness.commands.invoke import InvokeCommand
from harness.commands.list_commands import ListCommandsCommand
from harness.commands.list_models import ListModelsCommand
from harness.commands.ps import PSCommand
from harness.commands.switch_model import SwitchModelCommand
from harness.commands.switch_thinking_mode import SwitchThinkingModeCommand
from harness.commands.task import TaskCommand
from harness.tether import new_async_ollama_client
from markdown.display import display_text_as_markdown, new_markdown_console

HARNESS_COMMANDS: Sequence[type[AbstractHarnessCommand]] = [
    ListModelsCommand,
    SwitchModelCommand,
    SwitchThinkingModeCommand,
    InvokeCommand,
    TaskCommand,
    PSCommand,
    ListCommandsCommand,
]


async def yoke(client: AsyncClient, config: YokeConfig):

    console: Console = new_markdown_console()
    _model: str = config.ollama.default_model
    _think: bool = False
    registered_harness_commands: Sequence[AbstractHarnessCommand] = list()

    def update_setting(setting: str, value: Any) -> bool:
        nonlocal _model
        nonlocal _think

        match setting:
            case "model":
                _model = str(value)
            case "think":
                _think = value
            case _:
                return False

        return True

    def register_harness_commands(client: AsyncClient) -> None:
        registered_harness_commands.extend(
            [X(config, update_setting, client, console, registered_harness_commands) for X in HARNESS_COMMANDS]
        )

    register_harness_commands(client)

    async def execute_harness_command(command: str, args: list[str]):
        matching_command = [cmd for cmd in registered_harness_commands if cmd.command == command]
        if len(matching_command) == 0:
            display_text_as_markdown(console, f"unknown harness command: {command}")
            return

        harness_command = next(iter(matching_command))
        await harness_command.execute(_model, _think, args)

    while (invocation := input(f"\n{_model} > ").strip().lower()) not in ["exit", "quit"]:
        if len(invocation) == 0:
            continue

        match invocation.split(" "):
            case []:
                continue
            case [command, *args]:
                await execute_harness_command(command, args)


async def enyoke(config: YokeConfig):

    client = new_async_ollama_client(config.ollama.host, config.ollama.port)
    try:
        await yoke(client, config)
    except:
        traceback.print_exc()
        raise
    finally:
        await client.close()
