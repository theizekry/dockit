import os
import json
from typing import Dict, Optional, List
import questionary
from rich import print

class ServiceManager:
    def __init__(self):
        self.services_dir = "services"
        self.services = self.load_all_services()

    def load_all_services(self) -> Dict:
        """Load all available services from JSON files"""
        services = {}
        
        for service_name in os.listdir(self.services_dir):
            service_path = os.path.join(self.services_dir, service_name, "service.json")
            if os.path.exists(service_path):
                with open(service_path, 'r') as f:
                    services[service_name] = json.load(f)
        
        return services

    def get_service_versions(self, service_name: str) -> Optional[list]:
        """Get all available versions for a specific service"""
        if service_name in self.services:
            return list(self.services[service_name].keys())
        return None

    def get_service_config(self, service_name: str, version: str) -> Optional[dict]:
        """Get configuration for a specific service version"""
        if service_name in self.services and version in self.services[service_name]:
            return self.services[service_name][version]
        return None

    def validate_service_config(self, service_name: str, service_config: dict) -> bool:
        """Validate service configuration against its requirements"""
        # Check if service has either build or image
        if 'build' not in service_config and 'image' not in service_config:
            return False

        # Validate build configuration if present
        if 'build' in service_config:
            build = service_config['build']
            required_build_fields = ['base_image', 'command']
            for field in required_build_fields:
                if field not in build:
                    return False

        # Validate compose configuration
        if 'compose' not in service_config:
            return False

        return True

    def resolve_service_configs(self, selected_services: Dict[str, str]) -> Dict[str, dict]:
        """Resolve and validate service configurations for selected services and versions"""
        resolved = {}
        for service_name, version in selected_services.items():
            service_config = self.get_service_config(service_name, version)
            if service_config and self.validate_service_config(service_name, service_config):
                resolved[service_name] = service_config
        return resolved

    def collect_services(self) -> List[str]:
        """Collect user-selected services"""
        all_services = list(self.services.keys())
        return questionary.checkbox(
            "Select services to include:",
            choices=all_services
        ).ask()

    def collect_versions(self, selected_services: List[str]) -> Dict[str, str]:
        """Collect versions for selected services"""
        selected_versions = {}
        for service in selected_services:
            versions = self.get_service_versions(service)
            version = questionary.select(
                f"Select version for {service}:", choices=versions
            ).ask()
            selected_versions[service] = version
        return selected_versions

    def show_summary(self, selected_versions: Dict[str, str]) -> bool:
        """Show summary of selected services and versions"""
        print("Selected configuration:")
        for service, version in selected_versions.items():
            print(f"• {service} → {version}")
        return questionary.confirm("Proceed with generating configuration?", default=True).ask() 