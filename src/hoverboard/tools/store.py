from .tool import Tool


tools = {}


def register(tool: Tool):
    """
    Register a tool

    :param tool: The tool
    """
    tools[tool.name] = tool


def get(name: str) -> Tool:
    """
    Get a registered tool. Raises `KeyError` if the tool wasn't registered before.

    :param name: The name of the tool
    :return: The found `Tool` instance.
    """
    return tools[name]
