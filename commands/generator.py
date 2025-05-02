from assets.messenger import Messenger
from assets.debugger import Debugger
import os
import json
from jinja2 import Environment, FileSystemLoader
import click

class Generator:
    def __init__(self, selected_services: dict):
        """
        :param selected_services: dict like { "php": "8.2", "mysql": "8.0" }
        """
        self.selected_services = selected_services
        self.messenger = Messenger()
        self.env = Environment(
            loader=FileSystemLoader('templates'),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom dd filter
        self.env.filters['dd']   = Debugger.dd
        #self.env.filters['dd'] = Debugger.dump

    def run(self):
        self.messenger.sweet("🛠 Starting generation...")

        resolved = self.resolve_selected_services()

        if not self.validate_services(resolved):
            self.messenger.error("❌ Service validation failed. Please check your service configurations.")
            return

        self.generate_docker_compose(resolved)
        self.messenger.success("✅ Docker Compose file generated successfully!")

    def resolve_selected_services(self) -> dict:
        """Load service configurations from JSON files"""
        resolved = {}
        for service_name, version in self.selected_services.items():
            service_path = f"services/{service_name}/service.json"
            if not os.path.exists(service_path):
                self.messenger.error(f"❌ Service configuration not found: {service_path}")
                continue

            with open(service_path, 'r') as f:
                service_config = json.load(f)
                if version not in service_config:
                    self.messenger.error(f"❌ Version {version} not found for service {service_name}")
                    continue

                resolved[service_name] = service_config[version]

        return resolved

    def validate_services(self, services: dict) -> bool:
        """Validate service configurations against their requirements"""
        for service_name, service_config in services.items():
            self.messenger.info(f"Validating {service_name} configuration...")

            # Check if service has either build or image
            if 'build' not in service_config and 'image' not in service_config:
                self.messenger.error(f"❌ {service_name} must have either 'build' or 'image' configuration")
                return False

            # Validate build configuration if present
            if 'build' in service_config:
                build = service_config['build']
                required_build_fields = ['base_image', 'command']
                for field in required_build_fields:
                    if field not in build:
                        self.messenger.error(f"❌ {service_name} build configuration is missing required field: {field}")
                        return False

            # Validate compose configuration
            if 'compose' not in service_config:
                self.messenger.error(f"❌ {service_name} is missing 'compose' configuration")
                return False

        return True

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
                    # Generate Dockerfile
                    self.generate_dockerfile(service_name, service_config)
                    
                    # Update compose.build
                    service_config['compose']['build'] = {
                        'context': f"./dockit/{service_name}-{service_config['build']['base_image'].split(':')[1]}",
                        'dockerfile': "Dockerfile"
                    }
                else:
                    # Use direct image
                    service_config['compose']['image'] = service_config['image']
            
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
            
            click.echo(click.style('✓ Generated docker-compose.yml', fg='green'))
        except Exception as e:
            click.echo(click.style(f'Error generating docker-compose.yml: {str(e)}', fg='red'))

    def generate_dockerfile(self, service_name: str, service_config: dict):
        """Generate Dockerfile for a service"""
        try:
            # Get the template path
            template_path = f"Dockerfile.j2"
            
            # Render the Dockerfile template
            template = self.env.get_template(template_path)
            dockerfile = template.render(
                build=service_config['build']
            )
            
            # Create build directory
            build_dir = f"./dockit/{service_name}-{service_config['build']['base_image'].split(':')[1]}"
            os.makedirs(build_dir, exist_ok=True)
            
            # Write the Dockerfile
            with open(f"{build_dir}/Dockerfile", 'w') as f:
                f.write(dockerfile)
            
            click.echo(click.style(f'✓ Generated Dockerfile for {service_name}', fg='green'))
        except Exception as e:
            click.echo(click.style(f'Error generating Dockerfile for {service_name}: {str(e)}', fg='red'))
