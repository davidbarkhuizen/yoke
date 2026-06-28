import datetime

from model.model import Tool, ToolTag


async def get_current_date_time() -> str:
    """
    return the current system date-time as an iso-8601 format string

    Returns:
        A string corresponding to the current system date-time in ISO format YYYY-MM-DD HH:MM:SS.mmmmmm
    """

    return datetime.datetime.now().isoformat()


def new_tool() -> Tool:
    return Tool("get_current_date_time", get_current_date_time, [ToolTag.TEMPORAL])
