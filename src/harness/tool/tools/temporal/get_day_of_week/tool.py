import datetime

from model.model import Tool, ToolTag


async def get_day_of_week(iso8601_datum: str) -> str:
    """
    return the day of the week for the datum

    Args:
        datum: a datetime string in iso-8601 format (YYYY-MM-DD HH:MM:SS.mmmmmm)

    Returns:
        The corresponding day of the week, as a string
    """

    return datetime.datetime.fromisoformat(iso8601_datum).strftime("%A")


def new_tool() -> Tool:
    return Tool("get_day_of_week", get_day_of_week, [ToolTag.TEMPORAL])
