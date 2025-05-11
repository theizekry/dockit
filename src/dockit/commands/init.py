import questionary
from rich import print
from utilities.messenger import Messenger
from utilities.service_manager import ServiceManager
from utilities.gitignore_manager import GitignoreManager
from utilities.docker_manager import DockerManager
from commands.generator import Generator
import os

class InitCommand:
    def __init__(self):
        self.messenger = Messenger()
        self.service_manager = ServiceManager()
        self.gitignore_manager = GitignoreManager()
        self.docker_manager = DockerManager()
        self.service_manager.initialize_services()
        self.service_manager.load_all_services()
        
    def run(self):
        self.messenger.info("Dockit init")

        selected_services = self.service_manager.collect_services()
        if not selected_services:
            self.messenger.warning("No services selected. Exiting.")
            return

        selected_versions = self.service_manager.collect_versions(selected_services)

        confirmed = self.show_summary(selected_versions)
        if not confirmed:
            self.messenger.warning("Operation cancelled.")
            return

        # 🔥 Call the Generator
        generator = Generator(selected_versions)
        generator.run()

        # Update .gitignore if it exists
        self.gitignore_manager.add_pattern('dockit/data/', 'Dockit data directory')
        
        # Ask if user wants to start the containers
        if questionary.confirm("Would you like to start the containers now?", default=True).ask():
            self.docker_manager.start_containers()

    def show_summary(self, selected_versions):
        self.messenger.success("Selected configuration:")
        for service, version in selected_versions.items():
            print(f"• {service} → {version}")
        return questionary.confirm("Proceed with generating configuration?", default=True).ask()