# [Connect to multiple containers](https://code.visualstudio.com/remote/advancedcontainers/connect-multiple-containers#_connect-to-multiple-containers-in-multiple-vs-code-windows)

Currently you can only connect to one container per Visual Studio Code window. However, you can spin up multiple VS Code windows to attach to them.

If you'd prefer to use devcontainer.json instead and are using Docker Compose, you can create separate devcontainer.json files for each service in your source tree, each pointing to a common docker-compose.yml.

To see how this works, consider this example source tree:

```
📁 project-root
    📁 .git
    📁 .devcontainer
      📁 python-container
        📄 devcontainer.json
      📁 node-container
        📄 devcontainer.json
    📁 python-src
        📄 hello.py
    📁 node-src
        📄 hello.js
    📄 docker-compose.yml
```

The location of the .git folder is important, since we will need to ensure the containers can see this path for source control to work properly.

Next, assume the docker-compose.yml in the root is as follows:

```yaml
services:
  python-api:
    image: mcr.microsoft.com/devcontainers/python:1-3.12-bookworm
    volumes:
      # Mount the root folder that contains .git
      - .:/workspace
    command: sleep infinity
    # ...

  node-app:
    image: mcr.microsoft.com/devcontainers/typescript-node:1-20-bookworm
    volumes:
      # Mount the root folder that contains .git
      - .:/workspace
    command: sleep infinity
    # ...
```

You can then set up ./devcontainer/python-container/devcontainer.json for Python development as follows:

```json
{
  "name": "Python Container",
  "dockerComposeFile": ["../../docker-compose.yml"],
  "service": "python-api",
  "shutdownAction": "none",
  "workspaceFolder": "/workspace/python-src"
}
```

Next, you can set up ./devcontainer/node-container/devcontainer.json for Node.js development by changing workspaceFolder.

```json
{
  "name": "Node Container",
  "dockerComposeFile": ["../../docker-compose.yml"],
  "service": "node-app",
  "shutdownAction": "none",
  "workspaceFolder": "/workspace/node-src"
}
```

The "shutdownAction": "none" in the devcontainer.json files is optional, but will leave the containers running when VS Code closes -- which prevents you from accidentally shutting down both containers by closing one window.

### Connect to multiple containers in multiple VS Code windows

1. Open a VS Code window at the root level of the project.
2. Run Dev Containers: Reopen in Container from the Command Palette (F1) and select Python Container.
3. VS Code will then start up both containers, reload the current window and connect to the selected container.
4. Next, open a new window using File > New Window.
5. Open your project at root level in the current window.
6. Run Dev Containers: Reopen in Container from the Command Palette (F1) and select Node Container.
7. The current VS Code window will reload and connect to the selected container.

You can now interact with both containers from separate windows.

### [Extending a Docker Compose file when connecting to two containers]()

If you want to extend your Docker Compose file for development, you should use a single docker-compose.yml that extends both services (as needed) and is referenced in both devcontainer.json files.

For example, consider this docker-compose.devcontainer.yml file:

```yaml
services:
  python-api:
    volumes:
      - ~:~/local-home-folder # Additional bind mount
    # ...

  node-app:
    volumes:
      - ~/some-folder:~/some-folder # Additional bind mount
    # ...
```

Both `.devcontainer.json` files would be updated as follows:

```json
"dockerComposeFile": [
  "../../docker-compose.yml",
  "../../docker-compose.devcontainer.yml",
]
```

This list of compose files is used when starting the containers, so referencing different files in each devcontainer.json can have unexpected results.
