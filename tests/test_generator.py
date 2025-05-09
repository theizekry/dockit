import unittest
import os
import shutil
import json
from commands.generator import Generator
from utilities.service_manager import ServiceManager
from utilities.path_resolver import PathResolver
from utilities.messenger import Messenger

class TestGenerator(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        # Enable quiet mode for all tests
        Messenger.set_quiet(True)
        
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        self.services_dir = os.path.join(self.test_dir, 'services')
        self.templates_dir = os.path.join(self.test_dir, 'templates')
        
        # Create test directories
        os.makedirs(self.services_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Get the project root directory (two levels up from tests)
        project_root = os.path.dirname(os.path.dirname(__file__))
        
        # Copy actual service configuration
        source_service_dir = os.path.join(project_root, 'services', 'php')
        target_service_dir = os.path.join(self.services_dir, 'php')
        
        if os.path.exists(source_service_dir):
            shutil.copytree(source_service_dir, target_service_dir, dirs_exist_ok=True)
        else:
            raise FileNotFoundError(f"Service directory not found: {source_service_dir}")
            
        # Load the actual service configuration
        with open(os.path.join(target_service_dir, 'service.json'), 'r') as f:
            self.test_service = json.load(f)
            
        # Copy actual templates
        self.copy_actual_templates()

        # Patch PathResolver to use test paths
        self.original_services_dir = PathResolver.get_services_dir
        self.original_templates_dir = PathResolver.get_templates_dir
        PathResolver.get_services_dir = lambda: self.services_dir
        PathResolver.get_templates_dir = lambda: self.templates_dir

        # Initialize ServiceManager with test paths
        self.service_manager = ServiceManager()
        self.service_manager.services = {'php': self.test_service}

    def tearDown(self):
        """Clean up test environment after each test"""
        # Restore original PathResolver methods
        PathResolver.get_services_dir = self.original_services_dir
        PathResolver.get_templates_dir = self.original_templates_dir
        
        # Restore messenger quiet mode
        Messenger.set_quiet(False)
        
        # Clean up test directories and generated files
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except OSError:
                pass  # Ignore cleanup errors
                
        if os.path.exists('docker-compose.yml'):
            try:
                os.remove('docker-compose.yml')
            except OSError:
                pass  # Ignore cleanup errors
                
        if os.path.exists('dockit'):
            try:
                shutil.rmtree('dockit')
            except OSError:
                pass  # Ignore cleanup errors

    def copy_actual_templates(self):
        """Copy actual template files from the project"""
        # Get the project root directory (two levels up from tests)
        project_root = os.path.dirname(os.path.dirname(__file__))
        
        # Copy docker-compose template
        compose_template_path = os.path.join(project_root, 'templates', 'docker-compose.yml.j2')
        if os.path.exists(compose_template_path):
            shutil.copy2(compose_template_path, os.path.join(self.templates_dir, 'docker-compose.yml.j2'))
        else:
            raise FileNotFoundError(f"Template file not found: {compose_template_path}")

        # Copy Dockerfile template
        dockerfile_template_path = os.path.join(project_root, 'templates', 'Dockerfile.j2')
        if os.path.exists(dockerfile_template_path):
            shutil.copy2(dockerfile_template_path, os.path.join(self.templates_dir, 'Dockerfile.j2'))
        else:
            raise FileNotFoundError(f"Template file not found: {dockerfile_template_path}")

    def test_generate_docker_compose(self):
        """Test docker-compose generation"""
        generator = Generator({"php": "8.2"})
        generator.service_manager = self.service_manager
        generator.generate_docker_compose({"php": self.test_service["8.2"]})
        
        # Check if docker-compose.yml was created
        self.assertTrue(os.path.exists('docker-compose.yml'))
        
        # Check content
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
            self.assertIn('php:', content)
            self.assertIn('image: dockit-php-8.2', content)

    def test_generate_dockerfile(self):
        """Test Dockerfile generation"""
        generator = Generator({"php": "8.2"})
        generator.service_manager = self.service_manager
        generator.generate_dockerfile('php', self.test_service["8.2"])
        
        # Check if Dockerfile was created
        self.assertTrue(os.path.exists(os.path.join('dockit', 'php-8.2', 'Dockerfile')))
        
        # Check content
        with open(os.path.join('dockit', 'php-8.2', 'Dockerfile'), 'r') as f:
            content = f.read()
            self.assertIn('FROM php:8.2-fpm', content)
            self.assertIn('RUN apt-get install -y git', content)

    def test_run(self):
        """Test full generation process"""
        generator = Generator({"php": "8.2"})
        generator.service_manager = self.service_manager
        generator.run()
        
        # Check if all files were generated
        self.assertTrue(os.path.exists('docker-compose.yml'))
        self.assertTrue(os.path.exists(os.path.join('dockit', 'php-8.2', 'Dockerfile')))
        self.assertTrue(os.path.exists(os.path.join('dockit', 'php-8.2', 'php.ini')))

if __name__ == '__main__':
    unittest.main() 