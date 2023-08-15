# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Dict, List

import typer

app = typer.Typer()

# Define the project structure
PROJECT_STRUCTURE = {
    "pipelines": ["main.py"],
    "feature-store-python": {
        "features": ["features.py", "main.py"],
    },
    "ci": ["deploy.py"],
    ".env": None,
    ".gitignore": None,
    "pyproject.toml": None,
}


@app.command()
def init(
    project_path: str = typer.Argument(..., help="Path to initialize the project"),
):
    typer.echo("Initializing your ML application with Wyvern...")
    dfs_create_file(project_path, PROJECT_STRUCTURE)


@app.command()
def run():
    typer.echo("Running your ML application")


def create_file(file_path, content):
    if Path(file_path).exists():
        raise FileExistsError(f"File already exists: {file_path}")
    with open(file_path, "w") as f:
        f.write(content)


def dfs_create_file(path: str, structure: Dict | List | str | None = None) -> None:
    if structure is None:
        # create a file
        create_file(path, "")
    elif isinstance(structure, str):
        # create the directory with path
        Path(path).mkdir(parents=True, exist_ok=True)
        # create the child file
        create_file(os.path.join(path, structure), "")
    elif isinstance(structure, list):
        # create the directory with path
        Path(path).mkdir(parents=True, exist_ok=True)
        # create the child files
        for child in structure:
            if not isinstance(child, str):
                raise ValueError(f"Invalid value under {path}: {type(child)} - {child}")
            create_file(os.path.join(path, child), "")
    elif isinstance(structure, dict):
        # create the directory with path
        Path(path).mkdir(parents=True, exist_ok=True)
        # create the child files
        for child_path, child_structure in structure.items():
            dfs_create_file(os.path.join(path, child_path), child_structure)
    else:
        raise ValueError(f"Unknown type: {type(structure)} - {structure}")
