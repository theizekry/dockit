import questionary
from rich import print
from configs.services import SERVICES
from assets.messenger import Messenger
from commands.generator import Generator

class InitCommand:
    def __init__(self):
        self.messenger = Messenger()

    def run(self):
        self.messenger.info(f" 🛠 dockit init")

        selected_services = self.collect_services()
        if not selected_services:
            self.messenger.warning("No services selected. Exiting.")
            return

        selected_versions = self.collect_versions(selected_services)

        confirmed = self.show_summary(selected_versions)
        if not confirmed:
            self.messenger.warning("Operation cancelled.")
            return

        # 🔥 Call the Generator
        generator = Generator(selected_versions)
        generator.run()

    def collect_services(self):
        all_services = list(SERVICES.keys())
        return questionary.checkbox(
            "Select services to include:",
            choices=all_services
        ).ask()


    def collect_versions(self, selected_services):
        selected_versions = {}
        for service in selected_services:
            versions = list(SERVICES[service].keys())
            version = questionary.select(
                f"Select version for {service}:", choices=versions
            ).ask()
            selected_versions[service] = version
        return selected_versions


    def show_summary(self, selected_versions):
        self.messenger.success("Selected configuration:")
        for service, version in selected_versions.items():
            print(f"• {service} → {version}")
        return questionary.confirm("Proceed with generating configuration?", default=True).ask()
