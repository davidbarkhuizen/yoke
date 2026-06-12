from typing import Any

from ollama import AsyncClient

from config import LoomConfig, OllamaConfig
from harness_commands.abstract import AbstractSystemCommand
from harness_commands.active_model import ActiveModelCommand
from harness_commands.list_models import ListModelsCommand
from harness_commands.switch_model import SwitchModelCommand
from harness_commands.switch_thinking_mode import SwitchThinkingModeCommand
from model import ThinkingMode


def new_async_client(host: str, port: int) -> AsyncClient:
    url: str = f"http://{host}:{port}"
    return AsyncClient(host=url)


SYSTEM_COMMANDS = [ListModelsCommand, SwitchModelCommand, ActiveModelCommand, SwitchThinkingModeCommand]


async def weave(config: LoomConfig):
    print(config)

    host: str = config.ollama.host
    port: int = config.ollama.port
    client: AsyncClient = new_async_client(host, port)

    _model: str = config.model.model
    _thinking_mode: ThinkingMode = config.model.thinking_mode

    def get_active_config() -> OllamaConfig:
        return OllamaConfig(host=host, port=port)

    def reconfigure(setting: str, value: Any) -> bool:
        nonlocal _model
        nonlocal _thinking_mode

        match setting:
            case "model":
                _model = str(value)
            case "thinking_mode":
                _thinking_mode = [v for _, v in ThinkingMode.__members__.items() if v.value == value][0]
            case _:
                return False

        return True

    def register_system_commands(client: AsyncClient) -> list[AbstractSystemCommand]:
        return [X(client, get_active_config, reconfigure) for X in SYSTEM_COMMANDS]

    registered_system_commands = register_system_commands(client)

    def new_user_message(text: str) -> dict[str, str | None]:
        return {
            "content": text,
            "role": "user",
            "thinking": _thinking_mode.value if _thinking_mode != ThinkingMode.NO else None,
        }

    async def invoke(invocation: str) -> str:
        nonlocal _model

        message = new_user_message(invocation)

        stream = await client.chat(model=_model, messages=[message], stream=True)

        response_text: str = ""
        thinking_text: str = ""

        was_thinking: bool = False
        was_content: bool = False

        async for part in stream:
            with open("log.log", "a") as file:
                file.write(str(part) + "\n")

            thinking: str | None = part["message"].thinking
            if thinking:
                thinking_text += thinking
                if not was_thinking:
                    print()
                print(thinking, end="", flush=True)

            content: str = part["message"]["content"]
            if content:
                response_text += content
                if not was_content:
                    print(content, end="", flush=True)

            # try:
            #     done: bool = part["done"]
            #     done_reason: str | None = part.done_reason
            # except:
            #     print(part)
            #     import traceback

            #     tracek
            #     raise

            was_thinking: bool = thinking is not None
            was_content: bool = content != ""

        return response_text

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
