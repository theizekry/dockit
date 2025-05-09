import unittest
import os
import shutil
import json
from utilities.service_manager import ServiceManager
from utilities.path_resolver import PathResolver
from utilities.messenger import Messenger

class TestServiceManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        Messenger.set_quiet(True)

        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        self.services_dir = os.path.join(self.test_dir, 'services')
        self.templates_dir = os.path.join(self.test_dir, 'templates')

        os.makedirs(self.services_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)

        project_root = os.path.dirname(os.path.dirname(__file__))
        source_service_dir = os.path.join(project_root, 'services', 'php')
        target_service_dir = os.path.join(self.services_dir, 'php')

        if os.path.exists(source_service_dir):
            shutil.copytree(source_service_dir, target_service_dir, dirs_exist_ok=True)
        else:
            raise FileNotFoundError(f"Service directory not found: {source_service_dir}")

        # Load and clean test service config (remove priority if exists)
        with open(os.path.join(target_service_dir, 'service.json'), 'r') as f:
            self.test_service = json.load(f)
            self.test_service.pop("priority", None)

        # Patch PathResolver
        self.original_services_dir = PathResolver.get_services_dir
        self.original_templates_dir = PathResolver.get_templates_dir
        PathResolver.get_services_dir = lambda: self.services_dir
        PathResolver.get_templates_dir = lambda: self.templates_dir

    def tearDown(self):
        """Clean up test environment after each test"""
        PathResolver.get_services_dir = self.original_services_dir
        PathResolver.get_templates_dir = self.original_templates_dir
        Messenger.set_quiet(False)

        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except OSError:
                pass

    def test_initialize_services(self):
        """Test service initialization"""
        service_manager = ServiceManager()
        result = service_manager.initialize_services()
        self.assertFalse(result)  # Should return False if .dockit exists

    def test_load_all_services(self):
        """Test loading all services"""
        service_manager = ServiceManager()
        service_manager.load_all_services()
        self.assertIn('php', service_manager.services)
        self.assertEqual(service_manager.services['php'], self.test_service)

    def test_get_service(self):
        """Test getting a service"""
        service_manager = ServiceManager()
        service_manager.load_all_services()
        service = service_manager.get_service('php')
        self.assertEqual(service, self.test_service)

    def test_get_service_version(self):
        """Test getting a specific service version"""
        service_manager = ServiceManager()
        service_manager.load_all_services()
        version = service_manager.get_service_version('php', '8.2')
        self.assertEqual(version, self.test_service['8.2'])

    def test_get_service_versions(self):
        """Test getting all versions of a service"""
        service_manager = ServiceManager()
        service_manager.load_all_services()
        versions = service_manager.get_service_versions('php')
        expected_versions = ['8.4', '8.3', '8.2', '8.1', '8.0', '7.4']
        self.assertEqual(sorted(versions), sorted(expected_versions))

    def test_validate_service_config(self):
        """Test service configuration validation"""
        service_manager = ServiceManager()
        self.assertTrue(service_manager.validate_service_config('php', self.test_service['8.2']))
        invalid_config = {"compose": {}}
        self.assertFalse(service_manager.validate_service_config('php', invalid_config))

    def test_handle_service_files(self):
        """Test handling service files"""
        service_manager = ServiceManager()
        service_manager.handle_service_files('php', '8.2', self.test_service['8.2'])
        self.assertTrue(os.path.exists(os.path.join('dockit', 'php-8.2', 'php.ini')))

if __name__ == '__main__':
    unittest.main()
