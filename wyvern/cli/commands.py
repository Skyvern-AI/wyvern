# -*- coding: utf-8 -*-
import getpass
import importlib
import os
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Optional

import requests
import typer
import uvicorn
from humps.main import decamelize
from platformdirs import user_data_dir
from typing_extensions import Annotated

from wyvern import tracking

REDIS_VERSION = "redis-6.2.9"
app = typer.Typer()
WYVERN_TEMPLATE_URL = "https://codeload.github.com/Wyvern-AI/wyvern-starter/zip/main"
REDIS_URL = f"https://download.redis.io/releases/{REDIS_VERSION}.tar.gz"
REDIS_DIR = os.path.join(user_data_dir("redis_cli"), "redis")
REDIS_BIN = os.path.join(REDIS_DIR, REDIS_VERSION, "src", "redis-server")


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


def is_redis_installed():
    return os.path.exists(REDIS_BIN)


def is_redis_running():
    if platform.system().lower() == "windows":
        try:
            subprocess.run(
                ["tasklist"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except subprocess.CalledProcessError:
            return False
        return (
            "redis-server.exe"
            in subprocess.run(["tasklist"], stdout=subprocess.PIPE).stdout.decode()
        )

    else:  # For Unix-like systems (Linux, macOS)
        try:
            subprocess.run(
                ["ps", "-A"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except subprocess.CalledProcessError:
            return False
        return (
            "redis-server"
            in subprocess.run(["ps", "-A"], stdout=subprocess.PIPE).stdout.decode()
        )


def try_install_redis():
    if is_redis_installed():
        typer.echo("Redis is already installed.")
        return

    typer.echo(f"Installing Redis in {REDIS_DIR}...")
    os.makedirs(REDIS_DIR, exist_ok=True)
    subprocess.run(
        ["curl", "-L", REDIS_URL, "-o", os.path.join(REDIS_DIR, "redis.tar.gz")],
    )
    subprocess.run(
        ["tar", "xzvf", os.path.join(REDIS_DIR, "redis.tar.gz")],
        cwd=REDIS_DIR,
    )
    subprocess.run(["make"], cwd=os.path.join(REDIS_DIR, REDIS_VERSION))
    shutil.move(
        os.path.join(REDIS_DIR, REDIS_VERSION, "src", "redis-server"),
        REDIS_BIN,
    )


@app.command()
def init(
    project: str = typer.Argument(..., help="Name of the project"),
) -> None:
    """
    Initializes Wyvern application template code

    Args:
        project (str): Name of the project
    """

    # decamelize project name first
    project = decamelize(project)

    tracking.capture(event="oss_init_start")
    typer.echo("Initializing Wyvern application template code...")

    # validate project name
    if "/" in project:
        typer.echo("Error: Invalid project name. Project name cannot contain '/'")
        return

    if Path(project).exists():
        typer.echo(f"Error: Destination path '{project}' already exists.")
        return

    response = requests.get(WYVERN_TEMPLATE_URL)

    if response.status_code != 200:
        typer.echo(f"Error: Unable to download code from {WYVERN_TEMPLATE_URL}")
        return

    with open("temp.zip", "wb") as temp_zip:
        temp_zip.write(response.content)

    with zipfile.ZipFile("temp.zip", "r") as zip_ref:
        zip_ref.extractall(project)

    os.remove("temp.zip")
    # Flatten the extracted content into the destination directory
    extracted_dir = os.path.join(project, os.listdir(project)[0])
    for item in os.listdir(extracted_dir):
        item_path = os.path.join(extracted_dir, item)
        if os.path.isfile(item_path) or os.path.isdir(item_path):
            shutil.move(item_path, os.path.join(project, item))
    shutil.rmtree(extracted_dir)

    tracking.capture(event="oss_init_succeed")
    typer.echo(
        f"Successfully initialized Wyvern application template code in {project}",
    )


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
) -> None:
    """
    Starts Wyvern application server

    Example usage:
    wyvern run --path pipelines.main:app --host 0.0.0.0 --port 5001

    Args:
        path (str): path to the wyvern app. Default path is pipelines.main:app
        host (str): Host to run the application on. Default host is 0.0.0.0
        port (int): Port to run the application on. Default port is 5001
    """
    tracking.capture(event="oss_run_start")
    typer.echo("Running your ML application")
    # import the app from path
    try:
        sys.path.append(".")
        module_path, app_name = path.split(":")
        module = importlib.import_module(module_path)
    except ImportError:
        tracking.capture(event="oss_run_failed_import")
        typer.echo(f"Failed to import {path}")
        raise
    fastapi_app = getattr(module, app_name)
    config = uvicorn.Config(
        fastapi_app,
        host=host,
        port=port,
    )
    uvicorn_server = uvicorn.Server(config=config)
    tracking.capture(event="oss_run_succeed")
    uvicorn_server.run()


@app.command()
def redis() -> None:
    """Starts Redis server. This command will also install redis locally if it's not installed."""
    tracking.capture(event="oss_redis_start")
    try_install_redis()

    if is_redis_running():
        typer.echo("Redis is already running.")
        return

    typer.echo("Starting Redis...")
    tracking.capture(event="oss_redis_succeed")
    subprocess.run([REDIS_BIN])
