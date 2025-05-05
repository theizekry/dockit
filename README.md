# Dockit

Docker Service Configuration Generator

## Building from Source

1. Clone the repository:
```bash
git clone https://github.com/theizekry/dockit.git
cd dockit
```

2. Build the binary:
```bash
python build.py
```

The standalone binary will be created in the `dist` directory.

## Using the Binary

Simply run the binary:
```bash
./dockit
```

Available commands:
- `dockit init` - Initialize a new Docker service configuration
- `dockit add-service` - Add a new service
- `dockit delete-service` - Delete a service version
- `dockit about` - Show information about Dockit

## Features

- Easy service configuration management
- Support for multiple versions
- Direct image and build configurations
- Configuration file management
- Interactive CLI interface

## Author

theizekry
GitHub: https://github.com/theizekry 