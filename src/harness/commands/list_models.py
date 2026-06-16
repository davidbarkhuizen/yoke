from ollama._types import ListResponse

from harness.commands.abstract import AbstractHarnessCommand
from markdown.display import display_text_as_markdown
from markdown.render import dict_list_to_markdown_table


class ListModelsCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "list-models"

    async def execute(self, model: str, think: bool, args: list[str]) -> bool:
        response: ListResponse = await self.client.list()

        FIELDS_TO_EXCLUDE = ["modified_at", "parent_model", "families", "digest"]

        KEY_MAP: dict[str, str] = {"quantization_level": "quant", "parameter_size": "params"}
        model_dicts = [
            {KEY_MAP.get(k.lower(), k): v for k, v in model.__dict__.items() if k not in FIELDS_TO_EXCLUDE}
            for model in response.models
        ]

        for model_dict in model_dicts:
            model_dict["size"] = f"{str(int(model_dict['size']) // (1024 * 1024 * 1024)).ljust(3, ' ')} GB"
            model_details_object = model_dict.pop("details")
            model_details_dict = {
                KEY_MAP.get(k.lower(), k): v
                for k, v in model_details_object.__dict__.items()
                if k not in FIELDS_TO_EXCLUDE and isinstance(k, str)
            }
            model_dict.update(model_details_dict)

        model_dicts = sorted(model_dicts, key=lambda d: d["model"])
        display_text_as_markdown(
            self.console, dict_list_to_markdown_table(model_dicts, "right", column_order=["model"])
        )

        return True
