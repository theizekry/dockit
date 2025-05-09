import os
import sys
import shutil
import questionary
import typer
from utilities.messenger import Messenger
from utilities.service_manager import ServiceManager
from utilities.path_resolver import PathResolver

class PublishCommand:
    def __init__(self):
        self.messenger = Messenger()
        self.service_manager = ServiceManager()

    def run(self):
        """Run the publish command with force mode"""
        try:
            self.publish(True)
        except KeyboardInterrupt:
            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0)
        except Exception as e:
            self.messenger.error(f"An error occurred: {str(e)}")
            sys.exit(1)

    def publish(self, force: bool = False):
        """Publish services and templates with force option"""
        # Initialize directories first
        self.initialize_directories()
        
        # Track if any items were published
        services_published = self.publish_services(force)
        templates_published = self.publish_templates(force)
        
        # If nothing was published and force is False, show warning
        if not (services_published or templates_published) and not force:
            self.messenger.warning("No new items to publish. Use --force to overwrite existing items.")
            return False
            
        return True

    def publish_services(self, force: bool) -> bool:
        """Publish services to user's home directory"""
        predefined_services_path = PathResolver.get_predefined_services_path()
        if not os.path.exists(predefined_services_path):
            self.messenger.warning("No predefined services found")
            return False

        published = False
        for service_name in os.listdir(predefined_services_path):
            source_path = os.path.join(predefined_services_path, service_name)
            target_path = os.path.join(self.service_manager.services_dir, service_name)
            
            if os.path.isdir(source_path):
                if os.path.exists(target_path):
                    if force:
                        shutil.rmtree(target_path)
                        shutil.copytree(source_path, target_path)
                        self.messenger.info(f"Republished service: {service_name}")
                        published = True
                    else:
                        self.messenger.warning(f"Service already exists: {service_name}")
                else:
                    shutil.copytree(source_path, target_path)
                    #self.messenger.info(f"Published service: {service_name}")
                    published = True
        
        if published:
            self.messenger.success(f"Services published to {PathResolver.get_services_dir()}")
           
        return published

    def publish_templates(self, force: bool) -> bool:
        """Publish templates to user's home directory"""
        predefined_templates_path = PathResolver.get_predefined_templates_path()
        if not os.path.exists(predefined_templates_path):
            self.messenger.warning("No predefined templates found")
            return False

        published = False
        for template_name in os.listdir(predefined_templates_path):
            source_path = os.path.join(predefined_templates_path, template_name)
            target_path = os.path.join(self.service_manager.templates_dir, template_name)
            
            if os.path.isdir(source_path):
                if os.path.exists(target_path):
                    if force:
                        shutil.rmtree(target_path)
                        shutil.copytree(source_path, target_path)
                        self.messenger.info(f"Republished template: {template_name}")
                        published = True
                    else:
                        self.messenger.warning(f"Template already exists: {template_name}")
                else:
                    shutil.copytree(source_path, target_path)
                    published = True
            elif os.path.isfile(source_path):
                if os.path.exists(target_path):
                    if force:
                        shutil.copy2(source_path, target_path)
                        self.messenger.info(f"Republished template file: {template_name}")
                        published = True
                    else:
                        self.messenger.warning(f"Template file already exists: {template_name}")
                else:
                    shutil.copy2(source_path, target_path)
                    #self.messenger.info(f"Published template file: {template_name}")
                    published = True

        if published:
            self.messenger.success(f"Templates published to {PathResolver.get_templates_dir()}")
        
        return published

    def initialize_directories(self):
        """Initialize the base directories for services and templates"""
        os.makedirs(self.service_manager.services_dir, exist_ok=True)
        os.makedirs(self.service_manager.templates_dir, exist_ok=True)
        #self.messenger.info("Initialized base directories")
        
