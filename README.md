<h1 align="center">Wyvern</h1>

<div align="center">

**[Wyvern](https://docs.wyvern.ai) is an open source Machine Learning platform for marketplaces**

</div>

<div align="center">
  <img src="/docs/wyvern_logo.jpg" width="180px" alt="bentoml" />
</div>

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
