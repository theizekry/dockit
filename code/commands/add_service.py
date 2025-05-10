import os
import json
import sys
import questionary
from utilities.messenger import Messenger
from utilities.service_manager import ServiceManager
from utilities.path_resolver import PathResolver

class AddServiceCommand:
    def __init__(self):
        self.messenger = Messenger()
        self.service_manager = ServiceManager()
        self.services_dir = PathResolver.get_services_dir()
        self.templates_dir = PathResolver.get_templates_dir()

    def run(self):
        try:
            self.messenger.info("Adding a new service")

            # Get service name
            service_name = self._get_service_name()
            if not service_name:
                return

            # Get version type
            version_type = self._get_version_type()
            if not version_type:
                return

            # Get version
            version = self._get_version()
            if not version:
                return

            # Create service directory
            service_dir = os.path.join(self.services_dir, service_name)
            os.makedirs(service_dir, exist_ok=True)

            # Create conf directory
            conf_dir = os.path.join(service_dir, "conf")
            os.makedirs(conf_dir, exist_ok=True)

            # Create version directory
            version_dir = os.path.join(conf_dir, version)
            os.makedirs(version_dir, exist_ok=True)

            # Load skeleton template
            skeleton_file = "image_base.json" if version_type == "Docker Registry" else "build_version.json"
            skeleton_path = os.path.join(self.templates_dir, "skeletons", skeleton_file)
            with open(skeleton_path, "r") as f:
                skeleton = json.load(f)

            # Create or update service.json
            service_json_path = os.path.join(service_dir, "service.json")
            existing_config = {}
            if os.path.exists(service_json_path):
                with open(service_json_path, "r") as f:
                    existing_config = json.load(f)
                    if version in existing_config:
                        self.messenger.warning(f"Version '{version}' already exists for service '{service_name}'")
                        return

            # Add new version
            existing_config[version] = skeleton["version"]

            # Save service.json
            with open(service_json_path, "w") as f:
                json.dump(existing_config, f, indent=4)

            self.messenger.success(f"Service '{service_name}' added to {self.services_dir} successfully!")
            self.messenger.warning(f"You must configure the service before it can be used.\nEdit {service_json_path} to get started.")
        except KeyboardInterrupt:
            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0)
        except Exception as e:
            self.messenger.error(f"An error occurred: {str(e)}")
            sys.exit(1)

    def _get_service_name(self) -> str:
        """Get and validate service name"""
        try:
            while True:
                service_name = questionary.text(
                    "Enter service name (lowercase, alphanumeric, hyphens allowed):"
                ).ask()

                if not service_name:
                    self.messenger.warning("Service name cannot be empty")
                    continue

                if not service_name.replace('-', '').isalnum():
                    self.messenger.warning("Service name can only contain letters, numbers, and hyphens")
                    continue

                return service_name
        except KeyboardInterrupt:
            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0)

    def _get_version_type(self) -> str:
        """Get version type"""
        try:
            version_type = questionary.select(
                "Select version type:",
                choices=["Docker Registry", "Build Image"]
            ).ask()
            return version_type
        except KeyboardInterrupt:
            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0)

            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0)

    def _get_version(self) -> str:
        """Get and validate version"""
        try:
            while True:
                version = questionary.text(
                    "Enter version number (e.g., 1.25 or latest):"
                ).ask()

                if not version:
                    self.messenger.warning("Version cannot be empty")
                    continue

                return version
        except KeyboardInterrupt:
            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0) 