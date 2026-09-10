# Yoke

Yoke is a command-line harness for driving a local [Ollama](https://ollama.com)
language model through structured, file-based workflows. It keeps system prompts,
user specifications, input files, and generated outputs cleanly separated on
disk, and adds tool-calling, reusable task templates, and an interactive REPL on
top of the raw model.

## Requirements

- Python 3.10+
- A reachable Ollama server with at least one model pulled
- `arp-scan` (optional, only for the `arp-scan` helper in the launcher script)

Runtime dependencies are listed in `requirements.txt` (`ollama`, `httpx`,
`pydantic`, `dacite`, `aiofiles`, `rich`, `tabulate`); development dependencies
(`pytest`, `pytest-asyncio`) are in `requirements.dev.txt`.

## Install

The `yoke` launcher script wraps virtual-environment setup and execution:

```
. yoke install     # create .venv and install runtime + dev requirements
```

This creates `.venv/` in the repository root and installs everything into it.

## Configure

Configuration is read from `yoke.config.json` in the working directory. If the
file is missing it is created with defaults on first run.

```json
{
  "ollama": {
    "host": "localhost",
    "port": 11434,
    "default_model": "qwen3.6:35b-a3b"
  },
  "folders": {
    "system": "system",
    "user": "user"
  },
  "log": { "root_folder": "log" }
}
```

- `ollama.host` / `ollama.port` — where the Ollama server is listening
- `ollama.default_model` — the model selected at startup (change it at runtime
  with `use-model`)
- `folders.system` — root of the task template tree
- `folders.user` — root of user specifications and generated output

## Run

```
. yoke             # start the interactive harness
. yoke test        # run the pytest suite (from src/)
```

Starting the harness prints the command table and drops you at a prompt showing
the active model:

```
qwen3.6:35b-a3b >
```

Enter `exit` or `quit` to leave.

## Commands

| Command | Usage | Description |
| --- | --- | --- |
| `help` | `help` | Print the command table |
| `list-models` | `list-models` | List models available on the Ollama server |
| `list-tasks` | `list-tasks` | List task templates found under `system/task/` |
| `list-tools` | `list-tools` | List registered tools |
| `ps` | `ps` | Show models currently loaded by Ollama (`/api/ps`) |
| `use-model` | `use-model [model]` | Switch the active model for the session |
| `?` | `? [natural language query]` | One-shot query to the model (tool-calling enabled) |
| `dialog` | `dialog` | Multi-turn conversation with message history (tool-calling enabled) |
| `!` | `! [task-name] [user-specification]` | Run a task template against a user specification |
| `call-tool` | `call-tool [tool-name] [arguments-map]` | Invoke a registered tool directly |

Within `dialog`, enter `!new` to clear the conversation history or `!exit` to
return to the main prompt.

## Tasks

A task pairs a reusable **system prompt** with a **user specification**.

```
system/
└── task/
    └── <task-name>/
        └── system.md              # system prompt for the task

user/
└── task/
    └── <specification-name>/
        ├── specification.md       # the problem description
        ├── files/                 # optional supporting input files
        └── generated/
            └── <YYYYMMDD_HHMMSS>/  # one folder per run
```

Task names may be nested (any directory under `system/task/` containing a
`system.md`). Running `! <task-name> <specification-name>`:

1. Loads `system/task/<task-name>/system.md` as the system prompt.
2. Loads `user/task/<specification-name>/specification.md` and embeds every text
   file found under `user/task/<specification-name>/files/` into the prompt.
   Binary files are detected and skipped.
3. Sends the request to the active model via
   `prompt_and_handle_tool_calls()` in `src/harness/tether.py`.
4. Writes the response into a timestamped run folder (see [Output](#output)).

Task templates included in this repository:
`check-health`, `distill-specification`, `find-and-fix-bugs`, `summarise-code`,
`write-code`.

## Queries and dialog

`?` and `dialog` write their output under `user/query/<YYYYMMDD>/<HHMM_SS>/`
using the same artifact layout as tasks. `dialog` additionally carries a message
history across turns.

## Output

Each run folder may contain:

| File | Contents |
| --- | --- |
| `output.md` | The model's response text |
| `thinking.md` | The model's reasoning trace, when the model emits one |
| `message_history.json` | The full message list for the exchange |
| `stats.json` | Timing and token counts for the run |
| `files/` | Text files extracted from fenced code blocks in `output.md` |

## Tools

Tools are Python callables the model can invoke during `?` and `dialog` (and
directly via `call-tool`). Each tool lives at
`src/harness/tool/tools/<group>/<name>/tool.py` and exposes a `new_tool()`
factory returning a `Tool(function, tags)`.

`load_tools(tags)` discovers every tool on disk; passing a list of `ToolTag`
values filters to matching tools, while no argument (or an empty list) returns
all of them.

Tags: `ARITHMETIC`, `EXTERNAL`, `INTERNET`, `LLM`, `MATHEMATICS`, `QUERY`,
`SEARCH`, `TEMPORAL`.

Built-in tools:

| Tool | Tags | Notes |
| --- | --- | --- |
| `add`, `subtract`, `multiply`, `divide` | `MATHEMATICS`, `ARITHMETIC` | Basic arithmetic |
| `get_current_date_time`, `get_day_of_week` | `TEMPORAL` | Current date/time helpers |
| `search_internet` | `SEARCH`, `INTERNET` | DuckDuckGo Instant Answer API |
| `query_llm` | `QUERY`, `LLM`, `EXTERNAL` | Proxies a query to an external LLM service; endpoint configurable via `YOKE_QUERY_LLM_URL` (default `http://localhost:8081`) |

## Project layout

```
src/
├── entrypoint.py                  # starts the asyncio run loop
├── config.py                      # YokeConfig, JSON load/save
├── common/file_utils.py           # async file IO, binary detection
├── markdown/                      # parse / render / display markdown
├── model/model.py                 # dataclasses: Tool, RawPromptRequest, ...
└── harness/
    ├── yoke.py                    # command registry and REPL loop
    ├── tether.py                  # Ollama chat + tool-call handling
    ├── command/commands/          # one module per command
    └── tool/
        ├── tool_registry.py       # load_tools(), tag filtering
        ├── tool_logic.py          # call_tool()
        └── tools/                 # tool implementations

system/task/<name>/system.md       # task templates
user/task/<spec>/                  # user specifications and run output
user/query/<date>/                 # ? and dialog output
docs/                              # reference notes
setup/                             # Ollama / model setup notes
```
