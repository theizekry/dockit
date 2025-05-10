# Dockit CLI

>
> **Don’t copy old Docker files. Dockit them.**  
>

___

**# Dockit** is a developer-friendly CLI tool that helps you quickly scaffold and manage Docker-based services (like PHP, MySQL, Nginx, etc.) in your local development environment — with zero hassle.

- Add services with proper configuration
- Generate Docker Compose files in seconds

## Why to use Dockit CLI

**Starting a new project often means hunting down old Docker Compose files, remembering service versions, copying configs from previous local projects, or digging through GitHub repos. Dockit eliminates that repetitive setup pain by offering a guided workflow to build your stack from scratch — or even add new services to your dockit to use them in the future.**

---

## Installation

Install Dockit globally with `pip`:

```bash
pip install dockit-cli
```

## Requirements

- Python 3.11 or higher
- Docker installed and running
- Git (for version control)


## Usage

```bash
dockit init
```

This will walk you through setting up a new Docker environment with the services you choose.

> ### Add a new Service

```bash
dockit add-service
```

#### Pick from preconfigured services like:

* Nginx
* PHP
* MySQL
* PostgreSQL
* Redis
* MongoDB
* phpMyAdmin

---

## Documentation

[CHECKOUT DOCUMNETATION NOW](https://dockit.gitbook.io/docs)


## Test in a Clean Docker Container
Need to test it first? You can go with a simple container and checkout the tool instantly:
```bash
docker run -it --rm python:3.11-slim bash 

# inside bash run:

pip install dockit-cli

# start use the tool

dockit --help

# or 

dockit init

```
>This will let you try Dockit in isolation without affecting your local setup.

---

## 🧑‍💻 Contributing

We welcome contributions! Please read the [contribution guide](https://dockit.gitbook.io/docs/contribution) for setup instructions.

---

## 🪪 License
Dockit is open-source software licensed under the [MIT License](LICENSE).
