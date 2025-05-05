import typer
from commands.init import InitCommand
from commands.add_service import AddServiceCommand

class DockitCLI:
    def __init__(self):
        self.app = typer.Typer()
        self.init_cmd = InitCommand()
        self.add_service_cmd = AddServiceCommand()

        # Register the CLI commands
        self.app.command("init")(self.init_cmd.run)
        self.app.command("add-service")(self.add_service_cmd.run)

def main():
    DockitCLI().app()

if __name__ == "__main__":
    main()
