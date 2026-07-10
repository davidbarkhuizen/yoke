import asyncio
import traceback

from harness.command.abstract import AbstractHarnessCommand
from markdown.display import display_text_as_markdown


async def execute_harness_command(console, model: str, command: AbstractHarnessCommand, args: list[str]) -> bool:

    succeeded: bool = False
    try:
        succeeded = await command.execute(model, args)
    except ConnectionError:
        server: str = f"{command.config.ollama.host}:{command.config.ollama.port}"
        display_text_as_markdown(console, f"**error connecting to ollama server @ {server}**")
    except KeyboardInterrupt:
        pass
    except asyncio.exceptions.CancelledError:
        pass
    except Exception as e:
        stack_trace: str = "\n".join(traceback.format_exception(e))
        error_message: str = f"error: unhandled exception during harness command execution - {e} - {stack_trace}"
        display_text_as_markdown(console, error_message)

    display_text_as_markdown(console, "=" * 80)

    return succeeded
