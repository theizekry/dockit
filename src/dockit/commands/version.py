import sys
import re
import os
from pathlib import Path
from dockit.utilities.messenger import Messenger

class VersionCommand:
    def __init__(self):
        self.messenger = Messenger()

    def run(self):
        self.messenger.sweet(f"Dockit version: {self.get_version()}")
        return

    def get_version(self):
        """Reads the version from pyproject.toml"""
        # Traverse up until we find pyproject.toml
        current_dir = Path(__file__).resolve().parent
        while current_dir != current_dir.parent:
            candidate = current_dir / "pyproject.toml"
            if candidate.exists():
                with open(candidate, "r") as f:
                    content = f.read()
                m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                return m.group(1) if m else "Version not found"
            current_dir = current_dir.parent
        return "pyproject.toml not found"
 