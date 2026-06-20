from typing import Any

from ollama import AsyncClient, ChatResponse

from model.model import ChatMessageRole, PromptStats, RawPromptRequest, RawPromptResponse


def new_async_ollama_client(host: str, port: int) -> AsyncClient:
    return AsyncClient(host=f"http://{host}:{port}")


def new_message(role: str, text: str) -> dict[str, Any]:
    return {"content": text, "role": role}


async def prompt(client: AsyncClient, model: str, rq: RawPromptRequest) -> RawPromptResponse:

    system_prompt_length: int = len(rq.system_prompt)
    user_prompt_length: int = sum([len(text) for text in rq.user_prompt])
    total_prompt_length: int = system_prompt_length + user_prompt_length
    print(f"context length (chars): {total_prompt_length} = system {system_prompt_length} + user {user_prompt_length}")

    system_message = new_message(ChatMessageRole.system.value, rq.system_prompt)
    user_messages = [new_message(ChatMessageRole.user.value, text) for text in rq.user_prompt]
    messages: list[dict[str, Any]] = [system_message, *user_messages]

    response_text: str = ""
    thinking_text: str = ""
    stats: PromptStats | None = None

    chat_responses: list[ChatResponse] = list()

    try:
        async for chat_response in await client.chat(model=model, messages=messages, stream=True):
            chat_responses.append(chat_response)

            responding_model: str | None = chat_response.model
            if responding_model and responding_model != model:
                raise ValueError(
                    f"response model mismatch. requested a response from {model}, but actually received one from {responding_model}"
                )

            message = chat_response.get("message", None)
            if message is None:
                continue

            thinking: str | None = message.get("thinking", None)
            if thinking:
                thinking_text += thinking
                print(thinking, end="", flush=True)

            content: str = message.get("content", None)
            if content is not None:
                response_text += content
                print(content, end="", flush=True)

            done: bool = chat_response.get("done", False)
            if done:
                stats = PromptStats(
                    model=model,
                    done_reason=chat_response["done_reason"],
                    total_duration_s=chat_response["total_duration"] / 1e9,
                    load_duration_ms=chat_response["load_duration"] / 1e6,
                    prompt_eval_count=chat_response["prompt_eval_count"],
                    prompt_eval_duration_s=chat_response["prompt_eval_duration"] / 1e9,
                    eval_count=chat_response["eval_count"],
                    eval_duration_s=chat_response["eval_duration"] / 1e9,
                )
    except KeyboardInterrupt:
        return RawPromptResponse(content=response_text, thinking=thinking_text, stats=None)

    finally:
        with open("log.log", "a") as file:
            file.write("\n".join([str(rsp) for rsp in chat_responses]))

    print()
    if stats:
        print(
            f"{stats.prompt_eval_count} prompt tokens evaluated in {stats.prompt_eval_duration_s:.2f} seconds => {stats.tokens_in_per_second:.1f} tokens per second"
        )
        print(
            f"{stats.eval_count} tokens generated in {stats.eval_duration_s:.2f} seconds => {stats.tokens_out_per_second:.1f} tokens per second"
        )

    return RawPromptResponse(content=response_text, thinking=thinking_text, stats=stats)
