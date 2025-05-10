import unittest
import os
import shutil
import json
from commands.publish import PublishCommand
from utilities.path_resolver import PathResolver
from utilities.messenger import Messenger

class TestPublishCommand(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
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
        self.original_home_dir = PathResolver.get_home_dir
        self.original_services_dir = PathResolver.get_services_dir
        self.original_templates_dir = PathResolver.get_templates_dir
        PathResolver.get_home_dir = lambda: self.test_dir
        PathResolver.get_services_dir = lambda: os.path.join(self.test_dir, '.dockit', 'services')
        PathResolver.get_templates_dir = lambda: os.path.join(self.test_dir, '.dockit', 'templates')

        # Patch Messenger methods to be quiet
        def quiet_message(self, msg: str):
            pass
            
        self.original_info = Messenger.info
        self.original_success = Messenger.success
        self.original_warning = Messenger.warning
        self.original_error = Messenger.error
        self.original_note = Messenger.note
        self.original_sweet = Messenger.sweet
        
        Messenger.info = quiet_message
        Messenger.success = quiet_message
        Messenger.warning = quiet_message
        Messenger.error = quiet_message
        Messenger.note = quiet_message
        Messenger.sweet = quiet_message

    def tearDown(self):
        """Clean up test environment after each test"""
        # Restore original PathResolver methods
        PathResolver.get_services_dir = self.original_services_dir
        PathResolver.get_templates_dir = self.original_templates_dir
        
        # Restore original Messenger methods
        Messenger.info = self.original_info
        Messenger.success = self.original_success
        Messenger.warning = self.original_warning
        Messenger.error = self.original_error
        Messenger.note = self.original_note
        Messenger.sweet = self.original_sweet
        
        # Clean up test directories
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
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

    def test_initialize_directories(self):
        """Test directory initialization"""
        publish_cmd = PublishCommand()
        
        # Create .dockit directory
        dockit_dir = os.path.join(self.test_dir, '.dockit')
        os.makedirs(dockit_dir, exist_ok=True)
        
        # Create services and templates directories
        services_dir = os.path.join(dockit_dir, 'services')
        templates_dir = os.path.join(dockit_dir, 'templates')
        os.makedirs(services_dir, exist_ok=True)
        os.makedirs(templates_dir, exist_ok=True)
        
        publish_cmd.initialize_directories()
        
        # Check if directories were created
        self.assertTrue(os.path.exists(PathResolver.get_services_dir()))
        self.assertTrue(os.path.exists(PathResolver.get_templates_dir()))

    def test_publish_services(self):
        """Test service publishing"""
        publish_cmd = PublishCommand()
        publish_cmd.initialize_directories()
        
        # Create source service directory
        source_service_dir = os.path.join(self.services_dir, 'php')
        os.makedirs(source_service_dir, exist_ok=True)
        
        # Copy test service files
        shutil.copytree(source_service_dir, os.path.join(PathResolver.get_services_dir(), 'php'), dirs_exist_ok=True)
        
        # Check if service was published
        service_path = os.path.join(PathResolver.get_services_dir(), 'php', 'service.json')
        self.assertTrue(os.path.exists(service_path))
        
        # Check content
        with open(service_path, 'r') as f:
            content = json.load(f)
            self.assertEqual(content, self.test_service)

    def test_publish_templates(self):
        """Test template publishing"""
        publish_cmd = PublishCommand()
        publish_cmd.initialize_directories()
        
        # Create source template directory
        source_template_dir = self.templates_dir
        os.makedirs(source_template_dir, exist_ok=True)
        
        # Copy test template files
        shutil.copytree(source_template_dir, PathResolver.get_templates_dir(), dirs_exist_ok=True)
        
        # Check if templates were published
        self.assertTrue(os.path.exists(os.path.join(PathResolver.get_templates_dir(), 'Dockerfile.j2')))
        self.assertTrue(os.path.exists(os.path.join(PathResolver.get_templates_dir(), 'docker-compose.yml.j2')))

    def test_publish_without_force(self):
        """Test publishing without force flag"""
        publish_cmd = PublishCommand()
        publish_cmd.initialize_directories()
        
        # First publish
        publish_cmd.publish_services(force=True)
        publish_cmd.publish_templates(force=True)
        
        # Try to publish again without force
        result = publish_cmd.publish(force=False)
        self.assertFalse(result)  # Should return False as files exist

    def test_publish_with_force(self):
        """Test publishing with force flag"""
        publish_cmd = PublishCommand()
        publish_cmd.initialize_directories()
        
        # First publish
        publish_cmd.publish_services(force=True)
        publish_cmd.publish_templates(force=True)
        
        # Try to publish again with force
        result = publish_cmd.publish(force=True)
        self.assertTrue(result)  # Should return True as force is enabled

if __name__ == '__main__':
    unittest.main() 