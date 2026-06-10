from argparse import ArgumentParser
from dataclasses import dataclass


@dataclass
class CommandLineArgs:
    xxx: str


def parse_command_line_arguments() -> CommandLineArgs:

    parser: ArgumentParser = ArgumentParser(prog="yolo")
    parser.add_argument("xxx", action="store", type=str)

    args = parser.parse_args()

    return CommandLineArgs(xxx=args.xxx)
