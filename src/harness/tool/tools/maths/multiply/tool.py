from model.model import Tool, ToolTag


async def multiply(x: float, y: float) -> str:
    """
    return the product of two real numbers (floats)

    Args:
        x: first factor
        y: second factor

    Returns:
        The product of the two factors as a float
    """

    return str(x * y)


def new_tool() -> Tool:
    return Tool("multiply", multiply, [ToolTag.MATHEMATICS, ToolTag.ARITHMETIC])
