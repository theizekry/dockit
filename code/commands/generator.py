from utilities.messenger import Messenger
from utilities.debugger import Debugger
from utilities.service_manager import ServiceManager
import os
import json
from jinja2 import Environment, FileSystemLoader
from utilities.path_resolver import PathResolver
class Generator:
    def __init__(self, selected_services: dict):
        """
        :param selected_services: dict like { "php": "8.2", "mysql": "8.0" }
        """
        self.selected_services = selected_services
        self.messenger = Messenger()
        self.templates_dir = PathResolver.get_templates_dir()
        self.service_manager = ServiceManager()
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        # Add custom tojson filter with ensure_ascii=False
        self.env.filters['tojson'] = lambda value: json.dumps(value, ensure_ascii=False)
        # Add custom dd filter
        self.env.filters['dd'] = Debugger.dd

    def run(self):
        self.messenger.sweet("[+] Starting generation...")

        # Validate and resolve services before generation
        resolved = self.service_manager.resolve_service_configs(self.selected_services)
        if resolved is None:  # Explicitly check for None to handle validation failures
            self.messenger.error("Service validation failed. Operation cancelled.")
            return

        self.generate_docker_compose(resolved)
        self.messenger.success("Docker Compose file generated successfully!")

    def generate_docker_compose(self, services: dict):
        """Generate docker-compose.yml file based on selected services"""
        try:
            # Get current directory name as project name
            project_name = os.path.basename(os.getcwd())
            # Convert to slug format (lowercase, replace spaces with dashes)
            project_name = project_name.lower().replace(' ', '-')

            # Generate Dockerfiles and update compose configuration
            for service_name, service_config in services.items():

                if 'build' in service_config:
                    # we only need to set the image if the build is defined
                    service_config['image'] = f"dockit-{service_name}-{self.selected_services[service_name]}"

                    # Generate Dockerfile
                    self.generate_dockerfile(service_name, service_config)
                    
                    # Update compose.build using only the version number
                    version = service_config['build']['base_image'].split(':')[1].split('-')[0]
                    service_config['build'] = {
                        'context': f"./dockit/{service_name}-{version}",
                        'dockerfile': "Dockerfile",
                    }

                # Handle publishable files
                if 'publishable_files' in service_config:
                    if 'volumes' not in service_config['compose']:
                        service_config['compose']['volumes'] = []
                    
                    for file_config in service_config['publishable_files']:
                        # Add volume mapping
                        service_config['compose']['volumes'].append(
                            f"{file_config['source']}:{file_config['target']}"
                        )
                        
                        # Log the file mapping
                        self.messenger.info(f"Mapping {file_config['source']} to {file_config['target']}")

            # Render docker-compose template
            template = self.env.get_template('docker-compose.yml.j2')
            output = template.render(
                services=services,
                project_name=project_name
            )

            # Ensure the directory exists
            os.makedirs('.', exist_ok=True)
            
            # Write the docker-compose.yml file
            with open('docker-compose.yml', 'w') as f:
                f.write(output)
            
            self.messenger.info('Generated docker-compose.yml')
        except Exception as e:
            self.messenger.error(f"Error generating docker-compose.yml: {str(e)}")


    def generate_dockerfile(self, service_name: str, service_config: dict):
        """Generate Dockerfile for a service"""
        try:
            # Get the template path
            template_path = f"Dockerfile.j2"
            
            # Render the Dockerfile template
            template = self.env.get_template(template_path)
            dockerfile = template.render(
                build=service_config['build'],
                compose=service_config['compose']
            )
            
            # Create build directory using only the version number
            version = service_config['build']['base_image'].split(':')[1].split('-')[0]
            build_dir = f"./dockit/{service_name}-{version}"
            os.makedirs(build_dir, exist_ok=True)
            
            # Write the Dockerfile
            with open(f"{build_dir}/Dockerfile", 'w') as f:
                f.write(dockerfile)
            
            self.messenger.info(f'Generated Dockerfile for {service_name}')
        except Exception as e:
            self.messenger.error(f'Error generating Dockerfile for {service_name}: {str(e)}')
