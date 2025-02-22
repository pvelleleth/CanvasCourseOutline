import re
from typing import Dict, Callable, Any, List, get_type_hints
from pydantic import BaseModel

class ToolBox:
    def __init__(self):
        """Initialize an empty toolbox."""
        self.tools: Dict[str, Dict[str, Any]] = {}

    def add_tool(self, func: Callable):
        """
        Registers a function as a tool by extracting its name, docstring, and parameters.
        """
        func_name = func.__name__
        docstring = func.__doc__ or "No description provided."

        type_hints = get_type_hints(func)
        param_descriptions = self._extract_param_descriptions(docstring)

        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }

        for param_name, param_type in type_hints.items():
            if param_name == "return":
                continue  # Skip return type

            param_schema = {"type": self._map_type(param_type)}
            if param_name in param_descriptions:
                param_schema["description"] = param_descriptions[param_name]

            parameters["properties"][param_name] = param_schema
            parameters["required"].append(param_name)

        self.tools[func_name] = {
            "type": "function",
            "function": {
                "name": func_name,
                "description": self._extract_main_description(docstring),
                "parameters": parameters
            }
        }

    def update_tool(self, func: Callable):
        """
        Updates an existing tool definition.
        """
        if func.__name__ not in self.tools:
            raise ValueError(f"Tool '{func.__name__}' not found. Use add_tool() instead.")
        self.add_tool(func)

    def remove_tool(self, tool_name: str):
        """
        Removes a tool from the toolbox.
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
        else:
            raise ValueError(f"Tool '{tool_name}' not found.")

    def list_tools(self) -> List[str]:
        """
        Returns a list of all registered tools.
        """
        return list(self.tools.keys())

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Returns the tool definitions in OpenAI function calling format.
        """
        return list(self.tools.values())

    def _map_type(self, python_type: type) -> str:
        """
        Maps Python types to OpenAPI-compatible JSON types.
        """
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }
        return type_map.get(python_type, "string")  # Default to string if unknown

    def _extract_main_description(self, docstring: str) -> str:
        """
        Extracts the main function description from the docstring.
        """
        return docstring.split("\n")[0].strip() if docstring else "No description provided."

    def _extract_param_descriptions(self, docstring: str) -> Dict[str, str]:
        """
        Extracts parameter descriptions from a function docstring.

        Expected format:
        ```
        Function description.

        Parameters:
        location (str): The city and state, e.g., 'San Francisco, CA'.
        unit (str): Temperature unit ('Celsius' or 'Fahrenheit').
        ```
        """
        param_descriptions = {}
        param_pattern = re.compile(r"(\w+)\s*\(([^)]+)\):\s*(.+)")

        lines = docstring.split("\n")
        start_extracting = False

        for line in lines:
            line = line.strip()
            if line.lower().startswith("parameters:"):
                start_extracting = True
                continue

            if start_extracting:
                match = param_pattern.match(line)
                if match:
                    param_name, param_type, description = match.groups()
                    param_descriptions[param_name] = description

        return param_descriptions


# Example usage
toolbox = ToolBox()

# Define some tools with parameter descriptions
def get_temperature(location: str, unit: str) -> float:
    """
    Get the current temperature for a specific location.

    Parameters:
    location (str): The city and state, e.g., 'San Francisco, CA'.
    unit (str): Temperature unit ('Celsius' or 'Fahrenheit').
    """
    pass

def get_rain_probability(location: str) -> float:
    """
    Get the probability of rain for a specific location.

    Parameters:
    location (str): The city and state, e.g., 'San Francisco, CA'.
    """
    pass

toolbox.add_tool(get_temperature)
toolbox.add_tool(get_rain_probability)


import json
print(json.dumps(toolbox.get_tools(), indent=2))

print(toolbox.list_tools())

toolbox.remove_tool("get_rain_probability")
print(toolbox.list_tools())