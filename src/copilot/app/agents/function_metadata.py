from typing import Any, Callable, Dict, List, get_type_hints
import inspect
from dataclasses import dataclass
from datetime import date


@dataclass
class ParameterInfo:
    name: str
    type_hint: type
    description: str
    required: bool
    default: Any = None
    constraints: Dict[str, Any] = None


@dataclass
class FunctionSignature:
    name: str
    description: str
    parameters: List[ParameterInfo]
    return_type: type
    return_description: str


def extract_function_metadata(func: Callable) -> FunctionSignature:
    """Extract detailed function metadata including docstring information."""
    sig = inspect.signature(func)
    doc = inspect.getdoc(func)
    type_hints = get_type_hints(func)

    # Parse docstring for parameter and return descriptions
    param_descriptions = {}
    return_desc = ""
    if doc:
        current_section = None
        for line in doc.split("\n"):
            line = line.strip()
            if line.startswith("Parameters:"):
                current_section = "parameters"
            elif line.startswith("Returns:"):
                current_section = "returns"
            elif line and current_section == "parameters" and "-" in line:
                param_name = line.split("-")[0].strip()
                param_desc = line.split("-")[1].strip()
                param_descriptions[param_name] = param_desc
            elif line and current_section == "returns":
                return_desc += line + " "

    # Build parameter info list
    parameters = []
    for name, param in sig.parameters.items():
        param_type = type_hints.get(name, Any)
        parameters.append(
            ParameterInfo(
                name=name,
                type_hint=param_type,
                description=param_descriptions.get(name, ""),
                required=param.default == param.empty,
                default=(
                    None if param.default == param.empty else param.default
                ),
                constraints=get_type_constraints(param_type),
            )
        )

    return FunctionSignature(
        name=func.__name__,
        description=doc.split("\n")[0] if doc else "",
        parameters=parameters,
        return_type=type_hints.get("return", Any),
        return_description=return_desc.strip(),
    )


def get_type_constraints(type_hint: type) -> Dict[str, Any]:
    """Define constraints for specific types."""
    constraints = {}
    if type_hint == date:
        constraints["format"] = "YYYY-MM-DD"
    elif type_hint == float:
        constraints["type"] = "number"
    return constraints
