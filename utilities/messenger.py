from rich import print as rprint
from contextlib import contextmanager

class Messenger:
    _quiet = False  # Class-level quiet flag

    @classmethod
    def set_quiet(cls, quiet: bool = True):
        """Set the quiet mode for all messenger instances"""
        cls._quiet = quiet

    @classmethod
    @contextmanager
    def quiet_mode(cls):
        """Context manager for temporarily enabling quiet mode"""
        previous = cls._quiet
        cls._quiet = True
        try:
            yield
        finally:
            cls._quiet = previous

    def __init__(self, quiet: bool = None):
        """Initialize messenger with optional instance-level quiet setting"""
        self._instance_quiet = quiet

    @property
    def quiet(self) -> bool:
        """Get the effective quiet setting (instance-level if set, otherwise class-level)"""
        return self._instance_quiet if self._instance_quiet is not None else self._quiet

    def info(self, msg: str):
        if not self.quiet:
            rprint(f"[cyan][+] {msg}[/cyan]")

    def success(self, msg: str):
        if not self.quiet:
            rprint(f"[green][✓] {msg}[/green]")

    def warning(self, msg: str):
        if not self.quiet:
            rprint(f"[yellow][!] {msg}[/yellow]")

    def error(self, msg: str):
        if not self.quiet:
            rprint(f"[bold red][-] {msg}[/bold red]")

    def note(self, msg: str):
        if not self.quiet:
            rprint(f"[white][#] {msg}[/white]")

    def sweet(self, msg: str):
        if not self.quiet:
            rprint(f"[magenta]{msg}[/magenta]")

__all__ = ["Messenger"]
