#!/usr/bin/env python3
import os
import subprocess
import sys
import tarfile


def get_virtual_env() -> str | None:
    return os.environ.get("VIRTUAL_ENV")


def check_virtual_env(venv_name: str = "berenhak") -> str:
    venv_path = get_virtual_env()
    if venv_path is None:
        raise Exception(
            "No virtual environment is active. "
            f"Please activate '{venv_name}' first."
        )
    if os.path.basename(venv_path) != venv_name:
        raise Exception(
            f"Wrong virtual environment: '{os.path.basename(venv_path)}'. "
            f"Please activate '{venv_name}'."
        )
    return venv_path


def install_libraries() -> None:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    )


def get_installed_packages() -> list[str]:
    result = subprocess.check_output(
        [sys.executable, "-m", "pip", "freeze"]
    )
    packages = result.decode().strip().splitlines()
    return sorted(packages)


def save_requirements(packages: list[str]) -> None:
    with open("requirements.txt", "w") as f:
        f.write("\n".join(packages) + "\n")


def print_packages(packages: list[str]) -> None:
    for package in packages:
        print(package)


def archive_virtual_env(venv_path: str, venv_name: str = "berenhak") -> None:
    archive_name = f"{venv_name}.tar.gz"
    with tarfile.open(archive_name, "w:gz") as tar:
        tar.add(venv_path, arcname=venv_name)
    print(f"Virtual environment archived: {archive_name}")


if __name__ == '__main__':
    try:
        venv_path = check_virtual_env()
        install_libraries()
        packages = get_installed_packages()
        print_packages(packages)
        save_requirements(packages)
        archive_virtual_env(venv_path)
    except Exception as e:
        print(f"Error: {e}")