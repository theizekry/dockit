import os
import json
import sys
import questionary
from utilities.messenger import Messenger
from utilities.service_manager import ServiceManager
from utilities.path_resolver import PathResolver

class ViewServiceCommand:
    def __init__(self):
        self.messenger = Messenger()
        self.service_manager = ServiceManager()
        self.services_dir = PathResolver.get_services_dir()

    def run(self):
        try:
            self.messenger.info("Viewing service configuration")

            # Step 1: Load all services
            self.service_manager.load_all_services()

            # Step 2: Get available services formatted for prompt
            services = ServiceManager.format_services_for_prompt(list(self.service_manager.services.keys()))
            
            if not services:
                self.messenger.warning("No services found")
                return

            # Step 3: Ask user to select a service
            service_name = questionary.select(
                "Select a service to view:",
                choices=services
            ).ask()

            if not service_name:
                self.messenger.warning("No service selected")
                return

            # Step 4: Get available versions for selected service
            versions = self.service_manager.get_service_versions(service_name)
            if not versions:
                self.messenger.warning(f"No versions found for service '{service_name}'")
                return

            # Step 5: Ask user to select a version
            version = questionary.select(
                f"Select version of '{service_name}' to view:",
                choices=versions
            ).ask()

            if not version:
                self.messenger.warning("No version selected")
                return

            # Step 6: Get and show version config
            version_config = self.service_manager.get_service_config(service_name, version)
            if not version_config:
                self.messenger.error(f"No config found for {service_name} version {version}")
                return

            # Step 7: Show configuration
            self.messenger.info(f"\n📦 Configuration for {service_name} (version {version}):")
            self.messenger.info(json.dumps(version_config, indent=2))

        except KeyboardInterrupt:
            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0)
        except Exception as e:
            self.messenger.error(f"An error occurred: {str(e)}")
            sys.exit(1)
