# -*- coding: utf-8 -*-
import getpass
import importlib
import os
import shutil
import zipfile
from pathlib import Path
from typing import Optional

import requests
import typer
import uvicorn
from typing_extensions import Annotated

app = typer.Typer()
WYVERN_TEMPLATE_URL = "https://codeload.github.com/Wyvern-AI/wyvern-starter/zip/main"


def _replace_info(project: str, author: Optional[str] = None):
    toml_file_path = os.path.join(project, "pyproject.toml")
    if os.path.isfile(toml_file_path):
        author = author or getpass.getuser() or ""
        with open(toml_file_path, "r") as file:
            file_content = file.read()
        file_content = file_content.replace("wyvern-starter", project)
        file_content = file_content.replace('authors = [""]', f'authors = ["{author}"]')
        with open(toml_file_path, "w") as file:
            file.write(file_content)


@app.command()
def init(
    project: str = typer.Argument(..., help="Name and path to initialize the project"),
):
    typer.echo("Initializing Wyvern application template code...")
    if Path(project).exists():
        typer.echo(f"Error: Destination path '{project}' already exists.")
        return

    response = requests.get(WYVERN_TEMPLATE_URL)

    if response.status_code == 200:
        with open("temp.zip", "wb") as temp_zip:
            temp_zip.write(response.content)

        with zipfile.ZipFile("temp.zip", "r") as zip_ref:
            zip_ref.extractall(project)

        os.remove("temp.zip")
        # Flatten the extracted content into the destination directory
        extracted_dir = os.path.join(project, os.listdir(project)[0])
        for item in os.listdir(extracted_dir):
            item_path = os.path.join(extracted_dir, item)
            if os.path.isfile(item_path):
                shutil.move(item_path, os.path.join(project, item))
            elif os.path.isdir(item_path):
                shutil.move(item_path, os.path.join(project, item))
        shutil.rmtree(extracted_dir)

        # replace the project name in pyproject.toml
        _replace_info(project)

        typer.echo(
            f"Successfully initialized Wyvern application template code in {project}",
        )
    else:
        typer.echo(f"Error: Unable to download code from {WYVERN_TEMPLATE_URL}")


@app.command()
def run(
    path: str = "pipelines.main:app",
    host: Annotated[
        str,
        typer.Option(help="Host to run the application on"),
    ] = "0.0.0.0",
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
