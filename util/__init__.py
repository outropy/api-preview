import json
import os
from typing import Any

from rich.console import Console
from rich.syntax import Syntax

from outropy.copypasta.exceptions import IllegalArgumentError

console = Console()


def outropy_api_key() -> str:
    config_as_json = config_data()
    return config_as_json['OUTROPY_API_KEY']


def outropy_api_host() -> str:
    config_as_json = config_data()
    return config_as_json['OUTROPY_API_HOST']


def get_config(key: str) -> str:
    config_as_json = config_data()
    if key in config_as_json:
        return config_as_json[key]
    else:
        raise IllegalArgumentError(f"Key [{key}] not found in config.json: {config_as_json}")


def config_data() -> dict[str, str]:
    file_data = None
    # For convenience, try to find it all the way up to the root
    expected_file_name = 'config.json'
    path = expected_file_name
    while not os.path.exists(path):
        path = os.path.join('..', path)
        if os.path.abspath(path) == '/':
            raise FileNotFoundError("Could not find config.json file")

    file_data = open(path, "r")

    config_as_str = file_data.read()
    config_as_json = json.loads(config_as_str)
    return config_as_json  # type: ignore


def save_json_to_file(output_file: str, cotnent: Any) -> str:
    return save_text_to_file(output_file, json.dumps(cotnent, indent=4))


def save_text_to_file(output_file: str, text: str) -> str:
    with open(output_file, "w") as f:
        f.write(text)
    full_path = os.path.abspath(output_file)
    console.log(f"File saved to {full_path}")
    return full_path


def print_json(text: str) -> None:
    syntax = Syntax(text, "json", theme="monokai", line_numbers=True)  # Use syntax highlighting
    console.print(syntax)
