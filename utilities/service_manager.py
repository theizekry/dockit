import os
import json
import sys
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from questionary import Choice
import questionary
from utilities.messenger import Messenger
import fnmatch
from utilities.debugger import Debugger
from utilities.path_resolver import PathResolver

class ServiceManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.services = {}
        self.services_dir = PathResolver.get_services_dir()
        self.templates_dir = PathResolver.get_templates_dir()
        self.messenger = Messenger()
        self._initialized = True

    def initialize_services(self):
        """Initialize services directory and copy predefined services on first run"""
        # Get the base .dockit directory path
        dockit_base_dir = PathResolver.get_home_dir()
        
        # Check if this is first run by looking for .dockit directory
        if os.path.exists(dockit_base_dir) and os.path.exists(self.services_dir) and os.path.exists(self.templates_dir):
            return False

        # Use PublishCommand to handle initialization and publishing
        from commands.publish import PublishCommand
        PublishCommand().publish(force=False)
        return True

    def get_container_path(self, service_name: str, filename: str) -> str:
        """Get container path for a file based on service configuration"""
        
        service_config = self.services[service_name]
        
        # Check for exact matches first
        if filename in service_config['file_patterns']:
            return service_config['file_patterns'][filename]
        
        # Check for pattern matches
        for pattern, path in service_config['file_patterns'].items():
            if fnmatch.fnmatch(filename, pattern):
                return path.replace('{filename}', filename)
        
        # Use default path if no pattern matches
        return os.path.join(service_config['default_path'], filename)

    def scan_publishable_files(self, service_name: str, version: str, service_config: dict) -> list:
        """Scan for additional publishable files in the service directory"""
        publishable_files = []
        service_dir = os.path.join('services', service_name)
        
        # Only process files that are explicitly defined in the files array
        if 'publishes' in service_config:
            for file_name, file_config in service_config['publishes'].items():
                source_path = file_config['source'].format(version=version)
                full_source_path = os.path.join(service_dir, source_path)
                
                if os.path.exists(full_source_path):
                    publishable_files.append({
                        'source': full_source_path,
                        'target': file_config['destination']
                    })
                    self.messenger.info(f"Found publishable file: {source_path}")
                else:
                    self.messenger.warning(f"Configured file not found: {source_path}")
        
        return publishable_files

    def load_all_services(self):
        """Load all services from the services directory, sorted by priority descending."""
        if not os.path.exists(self.services_dir):
            os.makedirs(self.services_dir, exist_ok=True)
            return

        services_with_priority = []

        for service_name in os.listdir(self.services_dir):
            service_dir = os.path.join(self.services_dir, service_name)
            if os.path.isdir(service_dir):
                service_json = os.path.join(service_dir, "service.json")
                if os.path.exists(service_json):
                    with open(service_json, "r") as f:
                        data = json.load(f)
                        priority = data.pop("priority", 0)  # remove priority after reading it
                        services_with_priority.append((priority, service_name, data))

        # Sort by priority (descending)
        sorted_services = sorted(services_with_priority, key=lambda x: x[0], reverse=True)

        self.services = {
            service_name: data
            for _, service_name, data in sorted_services
        }

    def get_service(self, service_name):
        """Get service configuration"""
        return self.services.get(service_name)

    def get_service_version(self, service_name, version):
        """Get specific version of a service"""
        service = self.get_service(service_name)
        if service and version in service:
            return service[version]
        return None

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

    def handle_service_files(self, service_name: str, version: str, service_config: dict) -> None:
        """Handle service configuration files based on service configuration"""
        if 'publishes' not in service_config:
            return

        service_dir = os.path.join(self.services_dir, service_name)
        dockit_dir = os.path.join('dockit', f"{service_name}-{version}")

        # Ensure dockit directory exists
        os.makedirs(dockit_dir, exist_ok=True)

        # Initialize volumes list if not exists
        if 'volumes' not in service_config['compose']:
            service_config['compose']['volumes'] = []

        # Only process files that are explicitly defined in the files object
        for file_name, file_config in service_config['publishes'].items():
            # Get source and destination paths
            source_path = file_config['source'].format(version=version)
            destination_path = file_config['destination']
            
            # Construct full source path
            full_source_path = os.path.join(service_dir, source_path)
            
            # If file exists
            if os.path.exists(full_source_path):
                # Create target directory in dockit
                target_dir = os.path.dirname(os.path.join(dockit_dir, file_name))
                os.makedirs(target_dir, exist_ok=True)
                
                # Copy file
                target_file = os.path.join(dockit_dir, file_name)
                with open(full_source_path, 'r') as src, open(target_file, 'w') as dst:
                    dst.write(src.read())
                
                # Add volume mapping with relative path only if skipVolumes is not True
                if not file_config.get('skipVolumes', False):
                    relative_target = os.path.join('./dockit', f"{service_name}-{version}", file_name)
                    service_config['compose']['volumes'].append(
                        f"{relative_target}:{destination_path}"
                    )
                    self.messenger.info(f"Added file mapping: {relative_target} → {destination_path}")
            else:
                self.messenger.warning(f"File not found: {full_source_path}")

    def resolve_service_configs(self, selected_services: Dict[str, str]) -> Dict[str, dict]:
        """Resolve and validate service configurations for selected services and versions"""
        resolved = {}
        for service_name, version in selected_services.items():
            # Get service config
            service_config = self.get_service_config(service_name, version)
            if not service_config:
                self.messenger.error(f"Service configuration not found for {service_name} version {version}")
                return None

            # Validate service config
            if not self.validate_service_config(service_name, service_config):
                self.messenger.error(f"Invalid configuration for {service_name} version {version}.")
                return None

            # Handle service files
            self.handle_service_files(service_name, version, service_config)

            resolved[service_name] = service_config

        return resolved

    def collect_services(self) -> List[str]:
        """Collect user-selected services"""
        # Format service names to be more user-friendly
        formatted_services = {
            service: service.upper() if len(service) <= 4 else service.capitalize()
            for service in self.services.keys()
        }
        
        # Create choices with formatted names but return original service names
        choices = [
            Choice(
                title=formatted_name,
                value=original_name
            )
            for original_name, formatted_name in formatted_services.items()
        ]
        
        return questionary.checkbox(
            "Select services to include:",
            choices=choices
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
        self.messenger.info("Selected configuration:")
        for service, version in selected_versions.items():
            self.messenger.info(f"• {service} → {version}")
        return questionary.confirm("Proceed with generating configuration?", default=True).ask() 