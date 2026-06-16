import glob
import os
from pathlib import Path

from common.file_utils import file_is_binary, read_text_file_async, write_text_file_async
from harness.commands.abstract import AbstractHarnessCommand
from harness.tether import communicate
from markdown.display import display_text_as_markdown
from markdown.parse import extract_embedded_text_files_from_markdown
from markdown.render import dict_list_to_markdown_table, markdown_file_block_for_text_file
from model.model import CommunicationResponse, TextFile


async def context_file_block_from_file_paths(file_paths: list[str]) -> str:

    processed_file_count: int = 0
    embedded_file_count: int = 0
    binary_file_count: int = 0

    context = []
    for path in file_paths:
        try:
            processed_file_count = processed_file_count + 1
            if await file_is_binary(path):
                binary_file_count = binary_file_count + 1
                continue
            file_contents = await read_text_file_async(Path(path))

            encoded_file = markdown_file_block_for_text_file(TextFile(path, file_contents))

            context.extend(encoded_file.split("\n"))
            embedded_file_count = embedded_file_count + 1
            print(f"file {path} embedded into context file block")
        except:
            print(f"error reading file @ {path}")
            raise

    print(
        f"processed {processed_file_count} files, embedded {embedded_file_count}, ignored {binary_file_count} binary files"
    )

    return "\n".join(context)


def structured_user_text(user_files_block, user_text) -> str:

    return f"""
# user prompt

## files

{user_files_block}

## specification

{user_text}
"""


class TaskCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "task"

    @property
    def usage(self) -> str:
        return f"{self.command} [task-name] [user-specification]"

    async def execute(self, model: str, think: bool, args: list[str]) -> bool:

        if len(args) == 0:
            display_text_as_markdown(self.console, "error, no task specified. usage is: {self.usage}")
            return False

        task = args[0]

        task_specification_folder_path: Path = Path(self.config.folders.system) / "task" / task
        task_specification_file_path: Path = task_specification_folder_path / "system.md"

        if not os.path.exists(task_specification_file_path):
            display_text_as_markdown(self.console, f"error: **unknown task {task}**")
            return False

        if len(args) < 2:
            display_text_as_markdown(self.console, f"error: **no user specification for task**. usage is: {self.usage}")
            return False

        user_specification_name = args[1]

        user_specification_inputs_folder: Path = Path(self.config.folders.user) / user_specification_name
        user_specification_input_files_folder: Path = user_specification_inputs_folder / "files"
        glob_expression = f"{user_specification_input_files_folder.absolute()}/**/*.*"

        display_text_as_markdown(
            self.console,
            dict_list_to_markdown_table(
                [{"task": task, "model": model, "specification": user_specification_name}],
                alignment="left",
                column_order=["model", "task", "specification"],
            ),
        )

        task_specification_text: str
        try:
            task_specification_text = await read_text_file_async(task_specification_file_path)
        except FileNotFoundError:
            display_text_as_markdown(
                self.console,
                f"error: **system prompt file for task {task} does not exist**. expected @ {task_specification_file_path}",
            )
            return False

        user_spec_text_file_path: Path = user_specification_inputs_folder / "specification.md"
        user_specification_text: str
        try:
            user_specification_text = await read_text_file_async(user_spec_text_file_path)
        except FileNotFoundError:
            display_text_as_markdown(
                self.console,
                f"error, user specification file for task **{task}** does not exist @ **{user_spec_text_file_path}**",
            )
            return False

        user_files_block = await context_file_block_from_file_paths(glob.glob(glob_expression, recursive=True))

        rsp: CommunicationResponse = await communicate(
            client=self.client,
            model=model,
            system=task_specification_text,
            user=[structured_user_text(user_files_block=user_files_block, user_text=user_specification_text)],
            think=think,
        )

        thinking = rsp.thinking
        output_markdown_doc: str = rsp.content

        task_outputs_folder: Path = Path(self.config.folders.generated) / user_specification_name
        rsp_embedded_files_output_path: Path = task_outputs_folder / "files"

        if thinking:
            await write_text_file_async(task_outputs_folder / "thinking.md", rsp.thinking)

        response_text_files: list[TextFile] = extract_embedded_text_files_from_markdown(output_markdown_doc)

        os.makedirs(rsp_embedded_files_output_path, exist_ok=True)
        await write_text_file_async(task_outputs_folder / "output.md", output_markdown_doc)
        for text_file in response_text_files:
            await write_text_file_async(rsp_embedded_files_output_path / text_file.path, text_file.contents)

        print(f"extracted {len(response_text_files)} embedded text files:")
        for text_file in response_text_files:
            print(f"- {text_file.path}")

        # TODO stats
        #

        return True
