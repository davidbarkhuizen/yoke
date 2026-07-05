import os
from pathlib import Path

import aiofiles


async def file_is_binary(file_path: str, blocksize: int = 8192) -> bool:

    async with aiofiles.open(file_path, mode="rb") as file:
        chunk = await file.read(blocksize)

    return b"\x00" in chunk


async def read_text_file_async(file_path: Path):
    content: str = ""
    async with aiofiles.open(file_path, mode="tr") as file:
        content = await file.read()
    return content


async def write_text_file_async(file_path: Path, text: str):
    os.makedirs(file_path.parent, exist_ok=True)
    async with aiofiles.open(file_path, mode="tw") as file:
        await file.write(text)


async def write_lines_to_text_file_async(file_path: Path, lines: list[str]):
    return await write_text_file_async(file_path, "\n".join(lines))
