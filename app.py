import typer
from commands.init import InitCommand
from commands.add_service import AddServiceCommand
from commands.delete_service import DeleteServiceCommand
from commands.publish import PublishCommand
from commands.about import AboutCommand

class DockitCLI:
    def __init__(self):
        self.app = typer.Typer()
        self.init_cmd = InitCommand()
        self.add_service_cmd = AddServiceCommand()
        self.delete_service_cmd = DeleteServiceCommand()
        self.publish_cmd = PublishCommand()
        self.about_cmd = AboutCommand()

        # Register the CLI commands
        self.app.command("init")(self.init_cmd.run)
        self.app.command("add-service")(self.add_service_cmd.run)
        self.app.command("delete-service")(self.delete_service_cmd.run)
        self.app.command("force-publish")(self.publish_cmd.run)
        self.app.command("about")(self.about_cmd.run)

def main():
    DockitCLI().app()

if __name__ == "__main__":
    main()
