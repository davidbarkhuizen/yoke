from typing import Any

from ollama import AsyncClient

from model.model import ChatMessageRole, CommunicationResponse


def new_async_ollama_client(host: str, port: int) -> AsyncClient:
    return AsyncClient(host=f"http://{host}:{port}")


def new_message(role: str, text: str, think: bool) -> dict[str, Any]:
    return {"content": text, "role": role}


async def communicate(
    client: AsyncClient, model: str, system: str, user: list[str], think: bool
) -> CommunicationResponse:

    system_message = new_message(ChatMessageRole.system.value, system, think)
    user_messages = [new_message(ChatMessageRole.user.value, text, think) for text in user]

    messages: list[dict[str, Any]] = [system_message, *user_messages]

    response_text: str = ""
    thinking_text: str = ""

    stream = await client.chat(model=model, messages=messages, stream=True)

    with open("log.log", "a") as file:
        async for part in stream:
            file.write(str(part) + "\n")

            responding_model: str | None = part.model
            if responding_model and responding_model != model:
                raise ValueError(
                    f"response model mismatch. requested a response from {model}, but actually received one from {responding_model}"
                )

            # TODO validate that responing model matche requested model

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
