import asyncio
import glob
import json
import os
import traceback
from pathlib import Path

from common.file_utils import file_is_binary, read_text_file_async, write_text_file_async
from markdown.display import display_text_as_markdown
from markdown.parse import extract_embedded_text_files_from_markdown
from markdown.render import markdown_file_block_for_text_file
from model.model import BinaryFile, RawPromptRequest, RawPromptResponse, TextFile


def context_file_block_for_text_files(text_files: list[TextFile]) -> str:

    context = []
    for text_file in text_files:
        encoded_file = markdown_file_block_for_text_file(TextFile(text_file.path, text_file.text))
        context.extend(encoded_file.split("\n"))
        print(f"file {text_file.path} embedded into context file block")

    return "\n".join(context)


def structured_user_prompt(text: str, text_files: list[TextFile]) -> str:

    context_file_block = context_file_block_for_text_files(text_files)

    return f"""
# user prompt

## files

{context_file_block}

## text

{text}
"""


async def load_system_prompt_for_task_from_disk(console, tasks_root_folder_path: Path, task: str) -> str:

    task_system_prompt_folder_path: Path = tasks_root_folder_path / "task" / task
    task_system_prompt_file_path: Path = task_system_prompt_folder_path / "system.md"

    if not os.path.exists(task_system_prompt_file_path):
        error: str = f"error: **unknown task {task} (path does not exist at {task_system_prompt_file_path})**"
        display_text_as_markdown(console, error)
        raise ValueError(error)

    task_system_prompt_text: str
    try:
        task_system_prompt_text = await read_text_file_async(task_system_prompt_file_path)
    except FileNotFoundError:
        display_text_as_markdown(
            console,
            f"error: **system prompt file for task {task} does not exist**. expected @ {task_system_prompt_file_path}",
        )
        raise

    return task_system_prompt_text


async def load_user_prompt_for_task_from_disc(console, user_prompt_root_folder_path: Path) -> str:

    user_prompt_text_file_path: Path = user_prompt_root_folder_path / "specification.md"
    user_prompt_text: str
    try:
        user_prompt_text = await read_text_file_async(user_prompt_text_file_path)
    except FileNotFoundError:
        error: str = f"error: **user prompt test does not exist @  {user_prompt_root_folder_path}**"
        display_text_as_markdown(console, error)
        raise ValueError(error)

    async def context_file_for_file_path(file_path: str) -> TextFile | BinaryFile:
        if await file_is_binary(file_path):
            return BinaryFile(file_path)

        contents: str = await read_text_file_async(Path(file_path))
        return TextFile(path=file_path, text=contents)

    user_prompt_files_folder: Path = user_prompt_root_folder_path / "files"
    user_prompt_files_glob_expression = f"{user_prompt_files_folder}/**/*.*"
    user_prompt_file_paths: list[str] = glob.glob(user_prompt_files_glob_expression, recursive=True)
    user_prompt_context_files: list[TextFile | BinaryFile] = await asyncio.gather(
        *[context_file_for_file_path(file_path) for file_path in user_prompt_file_paths]
    )
    user_prompt_text_files = [
        context_file for context_file in user_prompt_context_files if isinstance(context_file, TextFile)
    ]

    return structured_user_prompt(text=user_prompt_text, text_files=user_prompt_text_files)


async def load_prompt_request_for_task_from_disk(
    console, tasks_root_folder_path: Path, user_prompt_root_folder_path: Path, task: str
) -> RawPromptRequest:
    system_prompt: str = await load_system_prompt_for_task_from_disk(console, tasks_root_folder_path, task)
    user_prompt: str = await load_user_prompt_for_task_from_disc(console, user_prompt_root_folder_path)

    return RawPromptRequest(system_prompt=system_prompt, user_prompt=[user_prompt])


async def write_prompt_response_elements_to_disk(rsp: RawPromptResponse, folder_path: Path) -> bool:

    try:
        if rsp.thinking:
            await write_text_file_async(folder_path / "thinking.md", rsp.thinking)

        await write_text_file_async(folder_path / "output.md", rsp.content)

        stats_file_str: str = json.dumps(rsp.stats.__dict__, indent=4)
        await write_text_file_async(folder_path / "stats.json", stats_file_str)

        embedded_text_files: list[TextFile] = extract_embedded_text_files_from_markdown(rsp.content)

        print(f"response contains {len(embedded_text_files)} embedded text files:")
        for text_file in embedded_text_files:
            print(f"- {text_file.path}")

        files_folder_path: Path = folder_path / "files"
        os.makedirs(files_folder_path, exist_ok=True)

        for text_file in embedded_text_files:
            await write_text_file_async(files_folder_path / text_file.path, text_file.text)

        return True

    except Exception as e:
        stack_trace: str = "\n".join(traceback.format_exception(e))
        error_message: str = f"error: unhandled exception writing response elements to disk - {e} - {stack_trace}"
        print(error_message)

        return False
