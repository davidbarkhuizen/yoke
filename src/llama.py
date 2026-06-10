from ollama import AsyncClient, ChatResponse


def new_client(url: str) -> AsyncClient:
    return AsyncClient(host=url)


async def connect_and_start_session(host: str, port: int, model: str):
    client: AsyncClient = new_client(f"http://{host}:{port}")

    message = {"content": "hello bot", "role": "user"}
    stream = await client.chat(model=model, messages=[message], stream=True)

    async for part in stream:
        content: str = part["message"]["content"]
        print(content, end="", flush=True)
