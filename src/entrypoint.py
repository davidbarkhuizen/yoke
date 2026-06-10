import asyncio

from config import Config, configure_from_json_file
from llama import connect_and_start_session

if __name__ == "__main__":
    config: Config = configure_from_json_file()
    print(config)

    asyncio.run(connect_and_start_session(config.ollama.host, config.ollama.port, config.ollama.model))
