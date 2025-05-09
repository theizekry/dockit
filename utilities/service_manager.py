import os
import json
import sys
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from questionary import Choice
import questionary
import fnmatch

from utilities.messenger import Messenger
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
        dockit_base_dir = PathResolver.get_home_dir()
        if os.path.exists(dockit_base_dir) and os.path.exists(self.services_dir) and os.path.exists(self.templates_dir):
            return False

        from commands.publish import PublishCommand
        PublishCommand().publish(force=False)
        return True

    def load_all_services(self):
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
                        priority = data.pop("priority", 0)
                        services_with_priority.append((priority, service_name, data))

        sorted_services = sorted(services_with_priority, key=lambda x: x[0], reverse=True)
        self.services = {
            service_name: data
            for _, service_name, data in sorted_services
        }

    def get_service(self, service_name):
        return self.services.get(service_name)

    def get_service_version(self, service_name, version):
        service = self.get_service(service_name)
        return service.get(version) if service and version in service else None

    def get_service_versions(self, service_name: str) -> Optional[list]:
        return list(self.services.get(service_name, {}).keys())

    def get_service_config(self, service_name: str, version: str) -> Optional[dict]:
        return self.services.get(service_name, {}).get(version)

    def validate_service_config(self, service_name: str, service_config: dict) -> bool:
        if 'build' not in service_config and 'image' not in service_config:
            return False
        if 'build' in service_config:
            build = service_config['build']
            required_build_fields = ['base_image', 'command']
            if not all(field in build for field in required_build_fields):
                return False
        return 'compose' in service_config

    def handle_service_files(self, service_name: str, version: str, service_config: dict) -> None:
        if 'publishes' not in service_config:
            return

        service_dir = os.path.join(self.services_dir, service_name)
        dockit_dir = os.path.join('dockit', f"{service_name}-{version}")
        os.makedirs(dockit_dir, exist_ok=True)

        if 'volumes' not in service_config['compose']:
            service_config['compose']['volumes'] = []

        for file_name, file_config in service_config['publishes'].items():
            source_path = file_config['source'].format(version=version)
            destination_path = file_config['destination']
            full_source_path = os.path.join(service_dir, source_path)

            if os.path.exists(full_source_path):
                target_dir = os.path.dirname(os.path.join(dockit_dir, file_name))
                os.makedirs(target_dir, exist_ok=True)

                with open(full_source_path, 'r') as src, open(os.path.join(dockit_dir, file_name), 'w') as dst:
                    dst.write(src.read())

                if not file_config.get('skipVolumes', False):
                    relative_target = os.path.join('./dockit', f"{service_name}-{version}", file_name)
                    service_config['compose']['volumes'].append(
                        f"{relative_target}:{destination_path}"
                    )
                    self.messenger.info(f"Added file mapping: {relative_target} → {destination_path}")
            else:
                self.messenger.warning(f"File not found: {full_source_path}")

    def resolve_service_configs(self, selected_services: Dict[str, str]) -> Dict[str, dict]:
        resolved = {}
        for service_name, version in selected_services.items():
            config = self.get_service_config(service_name, version)
            if not config:
                self.messenger.error(f"Service configuration not found for {service_name} version {version}")
                return None
            if not self.validate_service_config(service_name, config):
                self.messenger.error(f"Invalid configuration for {service_name} version {version}.")
                return None
            self.handle_service_files(service_name, version, config)
            resolved[service_name] = config
        return resolved

    def get_container_path(self, service_name: str, filename: str) -> str:
        config = self.services[service_name]
        if filename in config['file_patterns']:
            return config['file_patterns'][filename]
        for pattern, path in config['file_patterns'].items():
            if fnmatch.fnmatch(filename, pattern):
                return path.replace('{filename}', filename)
        return os.path.join(config['default_path'], filename)

    def scan_publishable_files(self, service_name: str, version: str, config: dict) -> list:
        files = []
        service_dir = os.path.join('services', service_name)
        if 'publishes' in config:
            for file_name, file_config in config['publishes'].items():
                source_path = file_config['source'].format(version=version)
                full_path = os.path.join(service_dir, source_path)
                if os.path.exists(full_path):
                    files.append({
                        'source': full_path,
                        'target': file_config['destination']
                    })
                    self.messenger.info(f"Found publishable file: {source_path}")
                else:
                    self.messenger.warning(f"Configured file not found: {source_path}")
        return files

    def collect_services(self) -> List[str]:
        choices = self.format_services_for_prompt(list(self.services.keys()))
        return questionary.checkbox("Select services to include:", choices=choices).ask()

    def collect_versions(self, selected_services: List[str]) -> Dict[str, str]:
        versions = {}
        for service in selected_services:
            version = self.select_version(service)
            versions[service] = version
        return versions

    def select_service(self) -> Optional[str]:
        choices = self.format_services_for_prompt(list(self.services.keys()))
        if not choices:
            self.messenger.warning("No services available.")
            return None
        return questionary.select("Select a service to view:", choices=choices).ask()

    def select_version(self, service_name: str) -> Optional[str]:
        versions = self.get_service_versions(service_name)
        if not versions:
            self.messenger.warning(f"No versions found for '{service_name}'")
            return None
        return questionary.select(f"Select version of '{service_name}':", choices=versions).ask()

    def show_summary(self, selected_versions: Dict[str, str]) -> bool:
        self.messenger.info("Selected configuration:")
        for service, version in selected_versions.items():
            self.messenger.info(f"• {service} → {version}")
        return questionary.confirm("Proceed with generating configuration?", default=True).ask()

    @staticmethod
    def format_services_for_prompt(services: List[str]) -> List[Choice]:
        return [
            Choice(
                title=service.upper() if len(service) <= 4 else service.capitalize(),
                value=service
            )
            for service in services
        ]
