"""Creates a Python project template, complete with readme, gitignore,
requirements files, flake8, black and pre-commit configuration files, and
(optionally) tests directory.
"""

import re
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional, List

url = (
    "https://gist.githubusercontent.com/vyhuholl/"
    "2c406f2b2509a15467a78d73f9aabead/"
    "raw/d974cb4bc790ae3107f62bdd0a7449763a1fd63b/"
)

repository_url_regex = re.compile(
    r"(git@|https://)[\w@-]*\.(com|org)[/:][\w/-]+/([\w-]+)\.git"
)

CONFIG_FILES = [
    ".flake8",
    ".gitignore",
    ".pre-commit-config.yaml",
    "pyproject.toml",
]


def is_repository_url(string: str) -> Optional[str]:
    """
    Check whether a string is a repository URL.

    Args:
        string: a string

    Return:
        repository name if a string is a repository URL, else None
    """
    if m := repository_url_regex.match(string):
        return m.group(3)

    return None


def create_file(path: Path, filename: str, content: str) -> None:
    """
    Creates a file with a given name and content in a given directory (if a
    file with this name does not already exists in the directory).

    Args:
        path: path to a directory
        filename: file name
        content: file content
    """
    if not (file_path := path / filename).exists():
        if content:
            with file_path.open("w") as file:
                file.write(content)


def run_commands(commands: List[List[str]]) -> None:
    """
    Runs a list of commands from a terminal. Exits Python, if a file was not
    found, a command did not return a successful return code or timed out.

    Args:
        commands: a list of commands, each command is a list of arguments
    """
    for command in commands:
        try:
            subprocess.run(command, check=True, timeout=60)
        except FileNotFoundError as exc:
            print(
                f"Command {command} failed because the process "
                f"could not be found.\n{exc}"
            )
            sys.exit()
        except subprocess.CalledProcessError as exc:
            print(
                f"Command {command} failed because the process "
                f"did not return a success return code.\n{exc}"
            )
            sys.exit()
        except subprocess.TimeoutExpired as exc:
            print(f"Command {command} timed out.\n{exc}")
            sys.exit()


def main(name: str, tests: bool) -> None:
    """
    Creates a Python project template, complete with readme, gitignore,
    requirements files, flake8, black and pre-commit configuration files, and
    (optionally) tests directory.

    Args:
        name: project name or an existing repository URL
        tests: whether to create tests directory
    """
    if is_url := is_repository_url(name):
        run_commands([["git", "clone", name]])
        name = is_url

    project_folder = Path().absolute() / name
    project_folder.mkdir(exist_ok=True)
    (project_folder / "requirements.txt").touch()
    create_file(project_folder, "requirements-dev.txt", "pre-commit")
    create_file(project_folder, "README.md", f"# {name}\n")

    if tests:
        tests_dir = project_folder / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "__init__.py").touch()

    commands = []

    for filename in CONFIG_FILES:
        if not (project_folder / filename).exists():
            commands.append(["wget", "-P", project_folder, url + filename])

    if not is_url:
        commands.append(["git", "-C", project_folder, "init", "b", "master"])

    commands += [
        ["git", "-C", project_folder, "add", "."],
        ["git", "-C", project_folder, "commit", "-m", "Initial commit"],
    ]

    if is_url:
        commands.append(["git", "-C", project_folder, "push"])

    run_commands(commands)


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="create_project", description="Create a Python project template."
    )

    parser.add_argument(
        "name", help="project name (or a link to an existing repository)"
    )

    parser.add_argument(
        "-t",
        "--tests",
        action="store_true",
        help="whether to create tests directory",
    )

    args = parser.parse_args()
    main(args.name, args.tests)
