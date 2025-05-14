import sys
import re
import os
from pathlib import Path
from dockit.utilities.messenger import Messenger
from importlib.util import find_spec

class VersionCommand:
    def __init__(self):
        self.messenger = Messenger()

    def run(self):
        self.messenger.sweet(f"Dockit version: {self.get_version()}")
        return

    def get_version(self):
        return "2.2.2"
            # """Reads the version from pyproject.toml within the installed package or dev path."""
            # try:
            #     package_path = Path(find_spec("dockit").origin).parent
            #     candidate = package_path.parent.parent / "pyproject.toml"
            #     if candidate.exists():
            #         with open(candidate) as f:
            #             content = f.read()
            #         match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            #         return match.group(1) if match else "Version not found"
            #     return "pyproject.toml not found"
            # except Exception as e:
            #     return f"Error reading version: {e}"
 