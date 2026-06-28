from model.model import Tool, ToolTag


async def subtract(minuend: float, subtrahend: float) -> str:
    """
    return the difference between two real numbers (floats)

    Args:
        x: minuend
        y: subtrahend

    Returns:
        The difference as a float
    """

    return str(minuend - subtrahend)


def new_tool() -> Tool:
    return Tool("subtract", subtract, [ToolTag.MATHEMATICS, ToolTag.ARITHMETIC])
