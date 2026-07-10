from __future__ import barry_as_FLUFL

import traceback
from typing import Any, Callable

import httpx
from ollama import AsyncClient, ChatResponse, Message

from harness.tool.tool_logic import call_tool
from markdown.display import display_text_as_markdown
from model.model import ChatRole, PromptStats, RawPromptRequest, RawPromptResponse, Tool


def new_async_ollama_client(host: str, port: int) -> AsyncClient:
    return AsyncClient(host=f"http://{host}:{port}")


def new_message(
    role: ChatRole, content: str, tool_calls: list[Message.ToolCall] | None = None, tool_name: str | None = None
) -> dict[str, Any]:
    core: dict[str, Any] = {"content": content, "role": role.value}

    if tool_calls is not None and len(tool_calls) > 0:
        core["tool_calls"] = tool_calls

    if tool_name is not None and len(tool_name) > 0:
        core["tool_name"] = tool_name

    return core


async def prompt(console, client: AsyncClient, model: str, rq: RawPromptRequest) -> RawPromptResponse:

    # system_prompt_length: int = len(rq.system_prompt)
    # user_prompt_length: int = sum([len(text) for text in rq.user_prompts])
    # total_prompt_length: int = system_prompt_length + user_prompt_length

    msg_history: list[dict[str, Any]] = [*rq.message_history]

    system_message = new_message(ChatRole.SYSTEM, rq.system_prompt, [])
    if len(rq.system_prompt) > 0:
        msg_history.append(system_message)

    user_messages = [new_message(ChatRole.USER, user_prompt, []) for user_prompt in rq.user_prompts]
    msg_history.extend(user_messages)

    # -------------------------------------------------

    rsp_content_text: str = ""
    rsp_thinking_text: str = ""
    rsp_tool_calls: list[Message.ToolCall] = list()
    rsp_stats: PromptStats | None = None

    chat_responses: list[ChatResponse] = list()

    def new_raw_prompt_response(
        failure_error: str | None = None, failure_stacktrace: str | None = None
    ) -> RawPromptResponse:

        msg_history.append(
            new_message(
                role=ChatRole.ASSISTENT,
                content=rsp_content_text,
                tool_calls=rsp_tool_calls,
            )
        )

        return RawPromptResponse(
            content=rsp_content_text,
            thinking=rsp_thinking_text,
            stats=rsp_stats,
            message_history=msg_history,
            tool_calls=rsp_tool_calls,
            failed=True if failure_error is not None else False,
            failure_error=failure_error if failure_error is not None else "",
            failure_stacktrace=failure_stacktrace if failure_stacktrace is not None else "",
        )

    tools: list[Callable] = [tool.function for tool in rq.tools]
    try:
        async for chat_response in await client.chat(model=model, messages=msg_history, tools=tools, stream=True):
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
                rsp_thinking_text += thinking
                print(thinking, end="", flush=True)

            content: str = message.get("content", None)
            if content is not None and content != "":
                if len(rsp_content_text) == 0:
                    print()
                    print("-" * 80)
                rsp_content_text += content
                print(content, end="", flush=True)

            tool_calls = message.get("tool_calls", None)
            if tool_calls is not None and len(tool_calls) > 0:
                rsp_tool_calls.extend(tool_calls)

            def safe_get(d: ChatResponse, key: str) -> float:
                if key not in d.__dict__.keys():
                    return 0

                v = d.get(key, 0)

                return v if v is not None else 0

            def safe_divide(dividend: float | None, divisor: float) -> float:
                if dividend is None:
                    return 0
                if dividend == 0:
                    return 0
                return dividend / divisor

            done: bool = chat_response.get("done", False)
            if done:
                rsp_stats = PromptStats(
                    model=model,
                    done_reason=chat_response["done_reason"],
                    total_duration_s=safe_divide(chat_response.get("total_duration", None), 1e9),
                    load_duration_ms=safe_divide(chat_response.get("load_duration", 0), 1e6),
                    prompt_eval_count=int(safe_get(chat_response, "prompt_eval_count")),
                    prompt_eval_duration_s=safe_divide(chat_response.get("prompt_eval_duration", None), 1e9),
                    eval_count=int(safe_get(chat_response, "eval_count")),
                    eval_duration_s=safe_divide(chat_response.get("eval_duration", 0), 1e9),
                )

    except httpx.ConnectError:
        error: str = "error connecting to ollama server"
        display_text_as_markdown(console, f"**{error}**")
        return new_raw_prompt_response(failure_error=error, failure_stacktrace=traceback.format_exc())

    finally:
        with open("log.log", "a") as file:
            file.write("\n".join([str(rsp) for rsp in chat_responses]))

    if rsp_content_text != 0:
        print()
        print("-" * 80)

    if rsp_stats:
        print(
            f"{rsp_stats.prompt_eval_count} prompt tokens evaluated in {rsp_stats.prompt_eval_duration_s:.2f} seconds => {rsp_stats.tokens_in_per_second:.1f} tokens per second"
        )
        print(
            f"{rsp_stats.eval_count} tokens generated in {rsp_stats.eval_duration_s:.2f} seconds => {rsp_stats.tokens_out_per_second:.1f} tokens per second"
        )

    return new_raw_prompt_response()


async def prompt_and_handle_tool_calls(
    console, client: AsyncClient, model: str, rq: RawPromptRequest, tools: list[Tool]
) -> RawPromptResponse:

    initial_rq = rq
    initial_rsp: RawPromptResponse = await prompt(console, client, model, initial_rq)

    message_history: list[dict[str, Any]] = list(initial_rsp.message_history)

    tool_calls: list[Message.ToolCall] = list(initial_rsp.tool_calls)
    rsp: RawPromptResponse = initial_rsp
    while len(tool_calls) > 0:
        tool_call_response_messages: list[dict[str, Any]] = []

        for tool_call in tool_calls:
            tool_call_response: str | None = await call_tool(console, tools, tool_call)
            tool_call_response_messages.append(
                new_message(role=ChatRole.TOOL, tool_name=tool_call.function.name, content=str(tool_call_response))
            )

        message_history.extend(tool_call_response_messages)

        rsp = await prompt(
            console,
            client,
            model,
            RawPromptRequest(system_prompt="", user_prompts=[], tools=tools, message_history=message_history),
        )
        tool_calls = [*rsp.tool_calls]
        message_history = rsp.message_history

    return rsp
