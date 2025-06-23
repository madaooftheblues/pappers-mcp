import json


def sum(a: int, b: int) -> int:
    return a + b


tools = [
    {
        "name": "sum",
        "description": "Sum two numbers",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"}
            },
            "required": ["a", "b"]
        }
    }
]


mapping_tool_function = {
    "sum": sum
}


def execute_tool(tool_name: str, tool_args):

    result = mapping_tool_function[tool_name](**tool_args)

    if result is None:
        result = "No result"
    elif isinstance(result, list):
        result = ' '.join(result)
    elif isinstance(result, dict):
        result = json.dumps(result)
    else:
        result = str(result)

    return result
