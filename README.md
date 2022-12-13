# Introduction
3D Data Science via Blender and Category Theory.

See [documentation](https://theNewFlesh.github.io/shot-glass/) for details.

# Installation
### Python
`pip install shot-glass`

### Docker
1. Install
   [docker](https://docs.docker.com/v17.09/engine/installation)
2. Install
   [docker-machine](https://docs.docker.com/machine/install-machine)
   (if running on macOS or Windows)
3. `docker pull theNewFlesh/shot-glass:[version]`
4. `docker run --rm --name shot-glass-prod --publish 2180:80 theNewFlesh/shot-glass:[version]`

### Docker For Developers
1. Install
   [docker](https://docs.docker.com/v17.09/engine/installation)
2. Install
   [docker-machine](https://docs.docker.com/machine/install-machine)
   (if running on macOS or Windows)
3. Ensure docker-machine has at least 4 GB of memory allocated to it.
4. `git clone git@github.com:theNewFlesh/shot-glass.git`
5. `cd shot-glass`
6. `chmod +x bin/shot-glass`
7. `bin/shot-glass start`

The service should take a few minutes to start up.

Run `bin/shot-glass --help` for more help on the command line tool.
