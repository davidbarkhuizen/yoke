import json
from dataclasses import asdict, dataclass, field
from typing import Any

from dacite import from_dict

CONFIG_FILE_PATH = "./config.json"


@dataclass
class LogConfig:
    root_folder: str = field(default_factory=lambda: "log")


@dataclass
class Ollama:
    host: str = field(default_factory=lambda: "localhost")
    port: int = field(default_factory=lambda: 11434)
    model: str = "llama3.2"


@dataclass
class Config:
    ollama: Ollama = field(default_factory=lambda: Ollama())
    log: LogConfig = field(default_factory=lambda: LogConfig())


def load_config_from_json_file(json_file_path: str) -> Config:

    data: dict[str, Any]
    with open(json_file_path) as f:
        data = json.load(f)

    config: Config = from_dict(data_class=Config, data=data)
    print(f"config loaded from file @ {json_file_path}")
    return config


def write_config_to_json_file(config: Config, json_file_path: str) -> None:
    with open(json_file_path, "w") as json_file:
        json.dump(asdict(config), json_file)


def load_config_from_file(config_file_path: str) -> Config | None:

    try:
        return load_config_from_json_file(config_file_path)
    except FileNotFoundError as e:
        print(f"exception attempting to load config file {config_file_path}: {e}")
        return None


def create_new_default_config(json_config_file_path: str) -> Config:
    config = Config()
    write_config_to_json_file(config=config, json_file_path=json_config_file_path)
    print(f"new config created at {json_config_file_path}")
    return config


def configure_from_json_file(json_config_file_path: str = CONFIG_FILE_PATH) -> Config:

    if (config := load_config_from_file(json_config_file_path)) is not None:
        return config

    print("not configured")
    return create_new_default_config(json_config_file_path)
