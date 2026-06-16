from ollama._types import ProcessResponse

from harness.commands.abstract import AbstractHarnessCommand
from markdown.display import display_text_as_markdown
from markdown.render import dict_list_to_markdown_table


class PSCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "ps"

    async def execute(self, model: str, think: bool, args: list[str]) -> bool:

        response: ProcessResponse = await self.client._request(ProcessResponse, "GET", "/api/ps")

        FIELDS_TO_EXCLUDE = [
            "modified_at",
            "parent_model",
            "families",
            "digest",
            "family",
            "format",
            "expires_at",
        ]

        model_dicts = [
            {k: v for k, v in model.__dict__.items() if k not in FIELDS_TO_EXCLUDE} for model in response.models
        ]

        for model_dict in model_dicts:
            model_dict["size"] = f"{int(model_dict['size']) // (1024 * 1024 * 1024)} GB"
            details_object = model_dict.pop("details")
            details = {k: v for k, v in details_object.__dict__.items() if k not in FIELDS_TO_EXCLUDE}
            model_dict.update(details)

        model_dicts = sorted(model_dicts, key=lambda d: d["model"])
        display_text_as_markdown(self.console, dict_list_to_markdown_table(model_dicts))

        return True
