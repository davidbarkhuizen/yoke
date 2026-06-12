from typing import Any

from ollama import AsyncClient

from config import OllamaConfig
from harness_commands.abstract import AbstractSystemCommand
from harness_commands.active_model import ActiveModelCommand
from harness_commands.list_models import ListModelsCommand
from harness_commands.switch_model import SwitchModelCommand


def new_async_client(host: str, port: int) -> AsyncClient:
    url: str = f"http://{host}:{port}"
    return AsyncClient(host=url)


SYSTEM_COMMANDS = [ListModelsCommand, SwitchModelCommand, ActiveModelCommand]


async def weave(host: str, port: int, model: str):
    client: AsyncClient = new_async_client(host, port)
    _model: str = model

    def get_config() -> OllamaConfig:
        return OllamaConfig(host=host, port=port, model=_model)

    def reconfigure(setting: str, value: Any) -> bool:
        nonlocal _model

        match setting:
            case "model":
                _model = str(value)
            case _:
                return False

        return True

    def register_system_commands(client: AsyncClient) -> list[AbstractSystemCommand]:
        return [X(client, get_config, reconfigure) for X in SYSTEM_COMMANDS]

    registered_system_commands = register_system_commands(client)

    async def invoke(invocation: str) -> str:
        nonlocal _model

        message = {"content": invocation, "role": "user"}

        stream = await client.chat(model=_model, messages=[message], stream=True)

        reply: str = ""

        async for part in stream:
            content: str | list[str] = part["message"]["content"]

            with open("log.log", "a") as file:
                file.write(str(part) + "\n")

            text: str = str(content)
            reply += text
            print(text, end="", flush=True)

        return reply

    async def execute_system_command(command: str, args: list[str]) -> list[str]:
        matching_command = [cmd for cmd in registered_system_commands if cmd.command == command]
        if len(matching_command) == 0:
            return [f"unknown system command: {command}"]

        system_command = next(iter(matching_command))
        return await system_command.execute(args)

    while (invocation := input("> ")) != "exit":
        if invocation.startswith("!"):
            command_text = invocation.strip()[1:]
            command_response: list[str]
            match command_text.split(" "):
                case []:
                    command_response = list(["empty harness command"])
                case [command, *args]:
                    command_response = await execute_system_command(command, args)
                case _:
                    command_response = list()
            for line in command_response:
                print(line)
        else:
            _ = await invoke(invocation)
            print()
