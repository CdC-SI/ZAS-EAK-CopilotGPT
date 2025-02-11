from typing import Any, Dict, Callable
import re
import ast

from agents.tools import CommandFunctions


class FunctionExecutor:
    def __init__(self):
        self._registered_functions: Dict[str, Callable] = {}
        self._command_functions = None

    def register_function(self, func: Callable) -> None:
        """Register a function that can be called via string."""
        self._registered_functions[func.__name__] = func

    def register_command_functions(
        self, command_functions: CommandFunctions
    ) -> None:
        """Register CommandFunctions instance for command execution"""
        self._command_functions = command_functions
        self.register_function(command_functions.translate_conversation)
        self.register_function(command_functions.summarize_conversation)

    def parse_function_call(self, function_string: str) -> tuple[str, list]:
        """
        Safely parse a function string like 'function_name(param1, param2)'
        Returns tuple of (function_name, [parameters])
        """
        # Extract function name and parameters string using regex
        match = re.match(r"(\w+)\((.*)\)", function_string.strip())
        if not match:
            raise ValueError(
                f"Invalid function string format: {function_string}"
            )

        func_name, params_str = match.groups()

        # Use ast.literal_eval to safely evaluate parameter strings
        if params_str.strip():
            try:
                # Wrap parameters in list brackets for ast.literal_eval
                params = ast.literal_eval(f"[{params_str}]")
            except (SyntaxError, ValueError) as e:
                raise ValueError(
                    f"Invalid parameters format: {params_str}"
                ) from e
        else:
            params = []

        return func_name, params

    async def execute(self, function_string: str) -> Any:
        """
        Execute a function from its string representation.
        Example: executor.execute('calculate_age("1990-01-01", 25)')
        """
        func_name, params = self.parse_function_call(function_string)

        if func_name not in self._registered_functions:
            raise ValueError(f"Function '{func_name}' is not registered")

        func = self._registered_functions[func_name]
        return await func(*params)
