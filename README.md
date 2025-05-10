# Dockit CLI

A powerful Docker management tool for developers that simplifies container management and service configuration.

## Installation

```bash
pip install dockit-cli
```

## Usage

```bash
# Initialize a new project
dockit init

# Add a new service
dockit add-service

# Delete a service
dockit delete-service

# Force publish changes
dockit force-publish

# Show about information
dockit about
```

## Features

- 🚀 Easy project initialization
- 🔧 Service management (add/delete)
- 📦 Docker container management
- 🎨 Rich terminal interface
- ⚡ Interactive CLI prompts
- 🔄 Version control integration

## Requirements

- Python 3.11 or higher
- Docker installed and running
- Git (for version control)

## Dependencies

- click>=8.0.0
- rich>=10.0.0
- docker>=6.0.0
- typer>=0.9.0
- questionary>=1.10.0
- jinja2>=3.0.0
- pyyaml>=6.0.0

## License

MIT License

___

**# Dockit** is a developer-friendly CLI tool that helps you quickly scaffold and manage Docker-based services (like PHP, MySQL, Nginx, etc.) in your local development environment — with zero hassle.

- Add services with proper configuration
- Generate Docker Compose files in seconds

## Why to use Dockit CLI

**Starting a new project often means hunting down old Docker Compose files, remembering service versions, copying configs from previous local projects, or digging through GitHub repos. Dockit eliminates that repetitive setup pain by offering a guided workflow to build your stack from scratch — or even add new services to your dockit to use them in the future.**

---

## 📚 Documentation

[Read the full docs here](https://dockit.gitbook.io/docs)


## Test in a Clean Docker Container
Need to test it first ? you can go with a simple container and checkout the tool.

```bash
docker run --rm -it python:3.11-slim bash -c "pip install dockit-cli && dockit --help"
```

---

## 🧑‍💻 Contributing

We welcome contributions! Please read the [contribution guide](https://dockit.gitbook.io/docs/contribution) for setup instructions.

---

## 🪪 License

Dockit is open-source software licensed under the [MIT License](LICENSE).
