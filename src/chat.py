from typing import Any

from ollama import AsyncClient

from model import ChatMessageRole, CommunicationResponse


def new_async_ollama_client(host: str, port: int) -> AsyncClient:
    url: str = f"http://{host}:{port}"
    return AsyncClient(host=url)


def new_message(role: str, text: str, think: bool) -> dict[str, Any]:
    return {"content": text, "role": role, "think": think}


async def communicate(
    client: AsyncClient, model: str, system: str, user: list[str], think: bool
) -> CommunicationResponse:

    system_message = new_message(ChatMessageRole.system.value, system, think)
    user_messages = [new_message(ChatMessageRole.user.value, text, think) for text in user]

    messages: list[dict[str, Any]] = [system_message, *user_messages]

    for message in messages:
        print("=-" * 40)
        print(message["role"])
        print(message["content"])

    print("=-" * 40)

    response_text: str = ""
    thinking_text: str = ""

    stream = await client.chat(model=model, messages=messages, stream=True)

    with open("log.log", "a") as file:
        async for part in stream:
            file.write(str(part) + "\n")

            message = part.get("message", None)
            if message is None:
                continue

            thinking: str | None = message.thinking
            if thinking:
                if not thinking_text:
                    print("\nThinking")
                    print("=-" * 40)

                thinking_text += thinking
                print(thinking, end="", flush=True)

            content: str = message.get("content", None)
            if content:
                if not response_text:
                    print("\nContent")
                    print("=-" * 40)

                response_text += content
                print(content, end="", flush=True)

            done: bool = bool(part.get("done", "False"))
            if done:
                pass
            # done_reason: str | None = part.done_reason

    print()

    return CommunicationResponse(content=response_text, thinking=thinking_text)
