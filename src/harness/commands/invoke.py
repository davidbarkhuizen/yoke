from harness.commands.abstract import AbstractHarnessCommand
from harness.tether import communicate
from model.model import CommunicationResponse


class InvokeCommand(AbstractHarnessCommand):
    @property
    def command(self) -> str:
        return "!"

    @property
    def usage(self) -> str:
        return "! [natural language instruction or query]"

    async def execute(self, model: str, think: bool, args: list[str]) -> bool:

        text = " ".join(args)

        _: CommunicationResponse = await communicate(
            client=self.client, model=model, system="", user=[text], think=think
        )

        return True
