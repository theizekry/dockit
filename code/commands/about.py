import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from utilities.messenger import Messenger

class AboutCommand:
    def __init__(self):
        self.messenger = Messenger()
        self.console = Console()

    def run(self):
        try:
            # Create a table for project info
            table = Table(show_header=False, box=None)
            table.add_row("Name", "Dockit")
            table.add_row("Description", "Docker Service Configuration Generator")
            table.add_row("Version", "1.0.0")
            table.add_row("Author", "theizekry")
            table.add_row("Date", "2025-05-05")
            table.add_row("GitHub", "https://github.com/theizekry")

            # Create a panel with the table
            panel = Panel(
                table,
                title="[bold blue]Dockit[/bold blue]",
                border_style="blue",
                padding=(1, 2)
            )

            # Display the panel
            self.console.print(panel)

            # Display additional information
            self.console.print("\n[bold]Features:[/bold]")
            self.console.print("• Easy service configuration management")
            self.console.print("• Support for multiple versions")
            self.console.print("• Docker Registry and build Image configurations")
            self.console.print("• Configuration file management")
            self.console.print("• Interactive CLI interface")

            self.console.print("\n[bold]Commands:[/bold]")
            self.console.print("• [blue]init[/blue] - Initialize a new Docker service configuration")
            self.console.print("• [blue]add-service[/blue] - Add a new service")
            self.console.print("• [blue]delete-service[/blue] - Delete a service version")

        except KeyboardInterrupt:
            self.messenger.info("\nOperation cancelled by user")
            sys.exit(0)
        except Exception as e:
            self.messenger.error(f"An error occurred: {str(e)}")
            sys.exit(1) 