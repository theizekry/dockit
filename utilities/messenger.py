from rich import print as rprint

class Messenger:
    def info(self, msg: str):
        rprint(f"[cyan][+] {msg}[/cyan]")

    def success(self, msg: str):
        rprint(f"[green]✓ {msg}[/green]")

    def warning(self, msg: str):
        rprint(f"[yellow][!] {msg}[/yellow]")

    def error(self, msg: str):
        rprint(f"[bold red][-] {msg}[/bold red]")

    def note(self, msg: str):
        rprint(f"[white]{msg}[/white]")

    def sweet(self, msg: str):
        rprint(f"[magenta]{msg}[/magenta]")

__all__ = ["Messenger"]
