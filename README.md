<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Setup](#setup)
  - [Set up PyEnv](#set-up-pyenv)
  - [Set up Poetry env](#set-up-poetry-env)
    - [1. Install Poetry](#1-install-poetry)
    - [2. Set up Poetry to create virtual envs in the local directory](#2-set-up-poetry-to-create-virtual-envs-in-the-local-directory)
    - [3. Python Version](#3-python-version)
    - [4. Set up the virtual environment](#4-set-up-the-virtual-environment)
    - [(Optional) 5. Set up auto-poetry shell spawning](#optional-5-set-up-auto-poetry-shell-spawning)
  - [Set up Pre-commit](#set-up-pre-commit)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Setup

This project is managed by Poetry

## Set up PyEnv

Install PyEnv using Brew:

```bash
brew install pyenv
```

Add this to your ~/.zshrc or ~/.bashrc depending on what you use. Documentation copied from [here](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv)

```bash
 export PYENV_ROOT="$HOME/.pyenv"
 command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
 eval "$(pyenv init -)"
```

## Set up Poetry env

### 1. Install Poetry

```bash
brew install poetry
```

### 2. Set up Poetry to create virtual envs in the local directory

```bash
poetry config virtualenvs.in-project true
```

### 3. Python Version

Poetry apparently has trouble initializing the Python version itself, so you'll have to force it to use the correct version

At the time of this writing, the correct version is 3.10, so just run:

```
poetry env use 3.10
```

And it'll switch the python version to the correct one. You only need to do this once

### 4. Set up the virtual environment

Have poetry set up all of the configs

```bash
poetry install
```

### (Optional) 5. Set up auto-poetry shell spawning

Add this to your ~/.zshrc:

This automatically spawns a new poetry shell whenever you `cd` into a directory with a poetry env

```bash
### Autoomatically activate virtual environment
function auto_poetry_shell {
    if [ -f "pyproject.toml" ] ; then
        source ./.venv/bin/activate
    fi
}

function cd {
    builtin cd "$@"
    auto_poetry_shell
}

auto_poetry_shell
```

## Set up Pre-commit

```bash
brew install pre-commit
pre-commit install
```
