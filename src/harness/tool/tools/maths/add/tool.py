from model.model import Tool, ToolTag


async def add(x: float, y: float) -> str:
    """
    returns the sum of two real numbers (floats)

    Args:
        x: first addend
        y: second addend

    Returns:
        A sum as a float
    """
    return str(x + y)


def new_tool() -> Tool:
    return Tool("add", add, [ToolTag.MATHEMATICS, ToolTag.ARITHMETIC])
