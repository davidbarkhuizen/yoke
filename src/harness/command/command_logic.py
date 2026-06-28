import asyncio
import traceback

from harness.command.abstract import AbstractHarnessCommand
from markdown.display import display_text_as_markdown


async def execute_harness_command(console, model: str, command: AbstractHarnessCommand, args: list[str]) -> bool:

    banner: list[str] = ["=" * 80, f"{command.name} {' '.join(args)}", ""]

    for banner_text in banner:
        display_text_as_markdown(console, banner_text)

    succeeded: bool = False
    try:
        succeeded = await command.execute(model, args)
    except ConnectionError:
        display_text_as_markdown(console, "**error connecting to ollama server**")
    except KeyboardInterrupt:
        display_text_as_markdown(console, "**keyboard interrupt**")
    except asyncio.exceptions.CancelledError:
        display_text_as_markdown(console, "**async cancelled error**")
        display_text_as_markdown(console, traceback.format_exc())
    except Exception as e:
        stack_trace: str = "\n".join(traceback.format_exception(e))
        error_message: str = f"error: unhandled exception during harness command execution - {e} - {stack_trace}"
        display_text_as_markdown(console, error_message)

    return succeeded
