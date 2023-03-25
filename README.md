<p>
    <a href="https://www.linkedin.com/in/alexandergbraun" rel="nofollow noreferrer">
        <img src="https://www.gomezaparicio.com/wp-content/uploads/2012/03/linkedin-logo-1-150x150.png"
             alt="linkedin" width="30px" height="30px"
        >
    </a>
    <a href="https://github.com/theNewFlesh" rel="nofollow noreferrer">
        <img src="https://tadeuzagallo.com/GithubPulse/assets/img/app-icon-github.png"
             alt="github" width="30px" height="30px"
        >
    </a>
    <a href="https://pypi.org/user/the-new-flesh" rel="nofollow noreferrer">
        <img src="https://cdn.iconscout.com/icon/free/png-256/python-2-226051.png"
             alt="pypi" width="30px" height="30px"
        >
    </a>
    <a href="http://vimeo.com/user3965452" rel="nofollow noreferrer">
        <img src="https://cdn.iconscout.com/icon/free/png-512/movie-52-151107.png?f=avif&w=512"
             alt="vimeo" width="30px" height="30px"
        >
    </a>
    <a href="http://www.alexgbraun.com" rel="nofollow noreferrer">
        <img src="https://i.ibb.co/fvyMkpM/logo.png"
             alt="alexgbraun" width="30px" height="30px"
        >
    </a>
</p>

<!-- <img id="logo" src="resources/icon.png" style="max-width: 717px"> -->

[![](https://img.shields.io/badge/License-MIT-F77E70?style=for-the-badge)](https://github.com/theNewFlesh/shot-glass/blob/master/LICENSE)
[![](https://img.shields.io/badge/3.10-F77E70?style=for-the-badge&label=Python&color=A0D17B&logo=python&logoColor=A0D17B)](https://github.com/theNewFlesh/shot-glass/blob/master/docker/config/pyproject.toml)
[![](https://img.shields.io/badge/0.1.0-5F95DE?style=for-the-badge&label=Version&color=5F95DE&logo=pypi&logoColor=5F95DE)](https://github.com/theNewFlesh/shot-glass/blob/master/docker/config/pyproject.toml)
<!-- [![](https://img.shields.io/pypi/pyversions/shot-glass?style=for-the-badge&label=Python&color=A0D17B&logo=python&logoColor=A0D17B)](https://github.com/theNewFlesh/shot-glass/blob/master/docker/config/pyproject.toml) -->
<!-- [![](https://img.shields.io/pypi/v/shot-glass?style=for-the-badge&label=PyPI&color=5F95DE&logo=pypi&logoColor=5F95DE)](https://pypi.org/project/shot-glass/) -->
<!-- [![](https://img.shields.io/pypi/dm/shot-glass?style=for-the-badge&label=Downloads&color=5F95DE)](https://pepy.tech/project/shot-glass) -->

# Introduction
3D Data Science via Blender and Category Theory.

See [documentation](https://theNewFlesh.github.io/shot-glass/) for details.

# Installation
### Python
`pip install shot-glass`

### Docker
1. Install [docker-desktop](https://docs.docker.com/desktop/)
2. `docker pull thenewflesh/shot-glass:latest`

### Docker For Developers
1. Install [docker-desktop](https://docs.docker.com/desktop/)
2. Ensure docker-desktop has at least 4 GB of memory allocated to it.
4. `git clone git@github.com:theNewFlesh/shot-glass.git`
5. `cd shot-glass`
6. `chmod +x bin/shot-glass`
7. `bin/shot-glass start`

The service should take a few minutes to start up.

Run `bin/shot-glass --help` for more help on the command line tool.

# Development CLI
bin/shot-glass is a command line interface (defined in cli.py) that works with
any version of python 2.7 and above, as it has no dependencies.

Its usage pattern is: `bin/shot-glass COMMAND [-a --args]=ARGS [-h --help] [--dryrun]`

### Commands

| Command              | Description                                                         |
| -------------------- | ------------------------------------------------------------------- |
| build-package        | Build production version of repo for publishing                     |
| build-prod           | Publish pip package of repo to PyPi                                 |
| build-publish        | Run production tests first then publish pip package of repo to PyPi |
| build-test           | Build test version of repo for prod testing                         |
| docker-build         | Build image of shot-glass                                           |
| docker-build-prod    | Build production image of shot-glass                                |
| docker-container     | Display the Docker container id of shot-glass                       |
| docker-coverage      | Generate coverage report for shot-glass                             |
| docker-destroy       | Shutdown shot-glass container and destroy its image                 |
| docker-destroy-prod  | Shutdown shot-glass production container and destroy its image      |
| docker-image         | Display the Docker image id of shot-glass                           |
| docker-prod          | Start shot-glass production container                               |
| docker-push          | Push shot-glass production image to Dockerhub                       |
| docker-remove        | Remove shot-glass Docker image                                      |
| docker-restart       | Restart shot-glass container                                        |
| docker-start         | Start shot-glass container                                          |
| docker-stop          | Stop shot-glass container                                           |
| docs                 | Generate sphinx documentation                                       |
| docs-architecture    | Generate architecture.svg diagram from all import statements        |
| docs-full            | Generate documentation, coverage report, diagram and code           |
| docs-metrics         | Generate code metrics report, plots and tables                      |
| library-add          | Add a given package to a given dependency group                     |
| library-graph-dev    | Graph dependencies in dev environment                               |
| library-graph-prod   | Graph dependencies in prod environment                              |
| library-install-dev  | Install all dependencies into dev environment                       |
| library-install-prod | Install all dependencies into prod environment                      |
| library-list-dev     | List packages in dev environment                                    |
| library-list-prod    | List packages in prod environment                                   |
| library-lock-dev     | Resolve dev.lock file                                               |
| library-lock-prod    | Resolve prod.lock file                                              |
| library-remove       | Remove a given package from a given dependency group                |
| library-search       | Search for pip packages                                             |
| library-sync-dev     | Sync dev environment with packages listed in dev.lock               |
| library-sync-prod    | Sync prod environment with packages listed in prod.lock             |
| library-update       | Update dev dependencies                                             |
| library-update-pdm   | Update PDM                                                          |
| session-lab          | Run jupyter lab server                                              |
| session-python       | Run python session with dev dependencies                            |
| state                | State of shot-glass                                                 |
| test-coverage        | Generate test coverage report                                       |
| test-dev             | Run all tests                                                       |
| test-fast            | Test all code excepts tests marked with SKIP_SLOWS_TESTS decorator  |
| test-lint            | Run linting and type checking                                       |
| test-prod            | Run tests across all support python versions                        |
| version              | Full resolution of repo: dependencies, linting, tests, docs, etc    |
| version-bump-major   | Bump pyproject major version                                        |
| version-bump-minor   | Bump pyproject minor version                                        |
| version-bump-patch   | Bump pyproject patch version                                        |
| zsh                  | Run ZSH session inside shot-glass container                         |
| zsh-complete         | Generate oh-my-zsh completions                                      |
| zsh-root             | Run ZSH session as root inside shot-glass container                 |

### Flags

| Short | Long      | Description                                          |
| ----- | --------- | ---------------------------------------------------- |
| -a    | --args    | Additional arguments, this can generally be ignored  |
| -h    | --help    | Prints command help message to stdout                |
| -     | --dryrun  | Prints command that would otherwise be run to stdout |
