import os
import sys
import json
import shutil
from pathlib import Path
import questionary
from rich import print
from utilities.messenger import Messenger
from utilities.service_manager import ServiceManager, get_resource_path
from commands.generator import Generator

class InitCommand:
    def __init__(self):
        self.messenger = Messenger()
        self.service_manager = ServiceManager()
        self.templates_dir = get_resource_path("templates")
        self.services_dir = get_resource_path("services")

    def run(self):
        try:
            # Create necessary directories
            os.makedirs(self.services_dir, exist_ok=True)
            os.makedirs(self.templates_dir, exist_ok=True)

            # Copy template files
            self.copy_template_files()

            self.messenger.success("Dockit initialized successfully!")
            self.messenger.info("You can now start adding services using 'dockit add-service'")

        except KeyboardInterrupt:
            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0)
        except Exception as e:
            self.messenger.error(f"An error occurred: {str(e)}")
            sys.exit(1)

    def copy_template_files(self):
        """Copy template files to the templates directory"""
        # Create template files
        templates = {
            "docker-compose.yml": """version: '3.8'

services:
  # Add your services here
""",
            "Dockerfile": """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
""",
            "requirements.txt": """flask==2.0.1
requests==2.26.0
"""
        }

        for filename, content in templates.items():
            filepath = os.path.join(self.templates_dir, filename)
            with open(filepath, "w") as f:
                f.write(content)

    def collect_services(self):
        all_services = list(self.service_manager.services.keys())
        return questionary.checkbox(
            "Select services to include:",
            choices=all_services
        ).ask()

    def collect_versions(self, selected_services):
        selected_versions = {}
        for service in selected_services:
            versions = self.service_manager.get_service_versions(service)
            version = questionary.select(
                f"Select version for {service}:", choices=versions
            ).ask()
            selected_versions[service] = version
        return selected_versions

    def show_summary(self, selected_versions):
        self.messenger.success("Selected configuration:")
        for service, version in selected_versions.items():
            print(f"• {service} → {version}")
        return questionary.confirm("Proceed with generating configuration?", default=True).ask()
