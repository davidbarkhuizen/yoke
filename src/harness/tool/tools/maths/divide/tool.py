from model.model import Tool, ToolTag


async def divide(dividend: float, divisor: float) -> str:
    """
    return the quotient of two real numbers (floats)

    Args:
        x: dividend
        y: divisor

    Returns:
        The quotient of the two numbers
    """

    return str(dividend / divisor)


def new_tool() -> Tool:
    return Tool("divide", divide, [ToolTag.MATHEMATICS, ToolTag.ARITHMETIC])
