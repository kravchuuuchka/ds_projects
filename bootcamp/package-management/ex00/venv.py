#!/usr/bin/env python3
import os


def get_virtual_env() -> str | None:
    return os.environ.get("VIRTUAL_ENV")


def print_virtual_env() -> None:
    venv_path = get_virtual_env()
    if venv_path is None:
        raise KeyError("VIRTUAL_ENV")
    print(f"Your current virtual env is {venv_path}")


if __name__ == '__main__':
    try:
        print_virtual_env()
    except KeyError as e:
        print(f"Environment variable {e} is not set. "
              "Is the virtual environment activated?")