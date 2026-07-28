from fastmcp import FastMCP
import random
# Create MCP server
mcp = FastMCP("Calculator Server")


@mcp.tool()
def add(a: float, b: float) -> float:
    """
    Add two numbers.

    Args:
        a: First number
        b: Second number
    """
    return a + b


@mcp.tool()
def generate_random_number() -> int:
    """
    Generate a random number between 1 and 100.
    """
    return random.randint(1, 100)

if __name__ == "__main__":
    mcp.run(transport="http",host="0.0.0.0",port=8000)