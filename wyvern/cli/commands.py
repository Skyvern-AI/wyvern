# -*- coding: utf-8 -*-
import importlib
import os
from pathlib import Path
from typing import Dict, List

import typer
import uvicorn
from typing_extensions import Annotated

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
}


@app.command()
def init(
    project_path: str = typer.Argument(..., help="Path to initialize the project"),
):
    typer.echo("Initializing your ML application with Wyvern...")
    dfs_create_file(project_path, PROJECT_STRUCTURE)


@app.command()
def run(
    path: str = "pipelines.main:app",
    host: Annotated[
        str,
        typer.Option(help="Host to run the application on"),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option(help="Port to run the application on. Default port is 5001"),
    ] = 5001,
):
    typer.echo("Running your ML application")
    # import the app from path
    try:
        module_path, app_name = path.split(":")
        module = importlib.import_module(module_path)
    except ImportError:
        typer.echo(f"Failed to import {path}")
        raise
    fastapi_app = getattr(module, app_name)
    config = uvicorn.Config(
        fastapi_app,
        host=host,
        port=port,
    )
    uvicorn_server = uvicorn.Server(config=config)
    uvicorn_server.run()


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
