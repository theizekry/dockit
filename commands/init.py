import questionary
from rich import print
import json
import os
from utilities.messenger import Messenger
from commands.generator import Generator

class InitCommand:
    def __init__(self):
        self.messenger = Messenger()
        self.services = self.load_services()

    def load_services(self) -> dict:
        """Load all available services from JSON files"""
        services = {}
        services_dir = "services"
        
        for service_name in os.listdir(services_dir):
            service_path = os.path.join(services_dir, service_name, "service.json")
            if os.path.exists(service_path):
                with open(service_path, 'r') as f:
                    services[service_name] = json.load(f)
        
        return services

    def run(self):
        self.messenger.info(f" 🛠 dockit init")

        selected_services = self.collect_services()
        if not selected_services:
            self.messenger.warning("No services selected. Exiting.")
            return

        selected_versions = self.collect_versions(selected_services)

        confirmed = self.show_summary(selected_versions)
        if not confirmed:
            self.messenger.warning("Operation cancelled.")
            return

        # 🔥 Call the Generator
        generator = Generator(selected_versions)
        generator.run()

    def collect_services(self):
        all_services = list(self.services.keys())
        return questionary.checkbox(
            "Select services to include:",
            choices=all_services
        ).ask()

    def collect_versions(self, selected_services):
        selected_versions = {}
        for service in selected_services:
            versions = list(self.services[service].keys())
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
