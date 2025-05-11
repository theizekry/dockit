import os
import json
import sys
import shutil
import questionary
from utilities.messenger import Messenger
from utilities.service_manager import ServiceManager
from utilities.path_resolver import PathResolver

class DeleteServiceCommand:
    def __init__(self):
        self.messenger = Messenger()
        self.service_manager = ServiceManager()
        self.services_dir = PathResolver.get_services_dir()

    def run(self):
        try:
            self.messenger.info("Deleting a service")

            # Get service name
            service_name = self._get_service_name()
            if not service_name:
                return

            # Get version to delete
            version = self._get_version(service_name)
            if not version:
                return

            # Ask about file deletion
            delete_files = self._confirm_file_deletion()
            if delete_files is None:
                return

            # Delete service version
            if not self._delete_service_version(service_name, version, delete_files):
                return

            self.messenger.success(f"Service version '{version}' deleted successfully!")

        except KeyboardInterrupt:
            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0)
        except Exception as e:
            self.messenger.error(f"An error occurred: {str(e)}")
            sys.exit(1)

    def _get_service_name(self) -> str:
        """Get and validate service name"""
        try:
            # Get list of available services
            services = []
            if os.path.exists(self.services_dir):
                services = [d for d in os.listdir(self.services_dir) 
                          if os.path.isdir(os.path.join(self.services_dir, d))]

            if not services:
                self.messenger.warning("No services found")
                return None

            # Let user select service
            service_name = questionary.select(
                "Select service to delete:",
                choices=services
            ).ask()

            return service_name
        except KeyboardInterrupt:
            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0)

    def _get_version(self, service_name: str) -> str:
        """Get and validate version to delete"""
        try:
            service_json_path = os.path.join(self.services_dir, service_name, "service.json")
            if not os.path.exists(service_json_path):
                self.messenger.error(f"Service configuration not found for '{service_name}'")
                return None

            with open(service_json_path, "r") as f:
                service_config = json.load(f)

            if not service_config:
                self.messenger.error(f"No versions found for service '{service_name}'")
                return None

            versions = list(service_config.keys())
            version = questionary.select(
                "Select version to delete:",
                choices=versions
            ).ask()

            return version
        except KeyboardInterrupt:
            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0)

    def _confirm_file_deletion(self) -> bool:
        """Ask user about file deletion"""
        try:
            return questionary.confirm(
                "Do you want to delete associated configuration files?",
                default=False
            ).ask()
        except KeyboardInterrupt:
            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0)

    def _delete_service_version(self, service_name: str, version: str, delete_files: bool) -> bool:
        """Delete service version and optionally its files"""
        try:
            service_dir = os.path.join(self.services_dir, service_name)
            service_json_path = os.path.join(service_dir, "service.json")
            version_dir = os.path.join(service_dir, "conf", version)

            # Load current configuration
            with open(service_json_path, "r") as f:
                service_config = json.load(f)

            # Get files to delete if needed
            files_to_delete = []
            if delete_files and version in service_config:
                version_config = service_config[version]
                if "files" in version_config:
                    for file_info in version_config["files"].values():
                        if "source" in file_info:
                            file_path = os.path.join(service_dir, file_info["source"].replace("{version}", version))
                            if os.path.exists(file_path):
                                files_to_delete.append(file_path)

            # Delete files if requested
            if delete_files:
                for file_path in files_to_delete:
                    try:
                        os.remove(file_path)
                        self.messenger.info(f"Deleted file: {file_path}")
                    except Exception as e:
                        self.messenger.warning(f"Failed to delete file {file_path}: {str(e)}")

                # Remove version directory if empty
                if os.path.exists(version_dir) and not os.listdir(version_dir):
                    shutil.rmtree(version_dir)
                    self.messenger.info(f"Removed empty version directory: {version_dir}")

            # Remove version from service.json
            del service_config[version]

            # Save updated service.json
            with open(service_json_path, "w") as f:
                json.dump(service_config, f, indent=4)

            # If no versions left, remove service directory
            if not service_config:
                shutil.rmtree(service_dir)
                self.messenger.info(f"Removed service directory: {service_dir}")

            return True

        except Exception as e:
            self.messenger.error(f"Failed to delete service version: {str(e)}")
            return False 