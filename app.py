import typer
from commands.init import InitCommand

class DockitCLI:
    def __init__(self):
        self.app = typer.Typer()
        self.init_cmd = InitCommand()

        # Register the CLI command
        self.app.command("init")(self.init_cmd.run)

def main():
    DockitCLI().app()

if __name__ == "__main__":
    main()
