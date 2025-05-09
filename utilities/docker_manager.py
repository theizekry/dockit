import subprocess
from utilities.messenger import Messenger

class DockerManager:
    def __init__(self):
        self.messenger = Messenger()

    def is_docker_installed(self) -> bool:
        """Check if Docker is installed and running"""
        try:
            subprocess.run(["docker", "info"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def start_containers(self) -> bool:
        """Start Docker containers in detached mode"""
        if not self.is_docker_installed():
            self.messenger.error("Docker not found. Please make sure Docker is installed and running.")
            return False

        try:
            self.messenger.info("Starting containers...")
            subprocess.run(["docker", "compose", "up", "-d"], check=True)
            self.messenger.success("Containers started successfully!")
            return True
        except subprocess.CalledProcessError as e:
            self.messenger.error(f"Failed to start containers: {str(e)}")
            return False

    def stop_containers(self) -> bool:
        """Stop running Docker containers"""
        if not self.is_docker_installed():
            self.messenger.error("Docker not found. Please make sure Docker is installed and running.")
            return False

        try:
            self.messenger.info("Stopping containers...")
            subprocess.run(["docker", "compose", "down"], check=True)
            self.messenger.success("Containers stopped successfully!")
            return True
        except subprocess.CalledProcessError as e:
            self.messenger.error(f"Failed to stop containers: {str(e)}")
            return False

    def get_container_status(self) -> dict:
        """Get status of all containers"""
        if not self.is_docker_installed():
            self.messenger.error("Docker not found. Please make sure Docker is installed and running.")
            return {}

        try:
            result = subprocess.run(
                ["docker", "compose", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.messenger.error(f"Failed to get container status: {str(e)}")
            return {}

    def rebuild_containers(self) -> bool:
        """Rebuild and restart containers"""
        if not self.is_docker_installed():
            self.messenger.error("Docker not found. Please make sure Docker is installed and running.")
            return False

        try:
            self.messenger.info("Rebuilding containers...")
            subprocess.run(["docker", "compose", "up", "-d", "--build"], check=True)
            self.messenger.success("Containers rebuilt successfully!")
            return True
        except subprocess.CalledProcessError as e:
            self.messenger.error(f"Failed to rebuild containers: {str(e)}")
            return False

__all__ = ["DockerManager"] 