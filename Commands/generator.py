from assets.messenger import Messenger
from assets.debugger import Debugger
from configs.services import SERVICES

class Generator:
    def __init__(self, selected_services: dict):
        """
        :param selected_services: dict like { "php": "8.2", "mysql": "8.0" }
        """
        self.selected_services = selected_services
        self.messenger = Messenger()


    def run(self):
        self.messenger.sweet("🛠 Starting generation...")

        resolved = self.resolve_selected_services()
        Debugger.dd(resolved)

        # TODO: process Dockerfiles, templates, docker-compose.yml


    def resolve_selected_services(self) -> dict:
        return {
            service: SERVICES[service][version]
            for service, version in self.selected_services.items()
        }
