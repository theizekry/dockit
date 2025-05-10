#!/usr/bin/env python3
import sys
import re
from pathlib import Path

def read_pyproject():
    with open('pyproject.toml', 'r') as f:
        return f.read()

def write_pyproject(content):
    with open('pyproject.toml', 'w') as f:
        f.write(content)

def bump_version(version_type):
    content = read_pyproject()
    version_pattern = r'version = "(\d+)\.(\d+)\.(\d+)"'
    match = re.search(version_pattern, content)
    
    if not match:
        print("Could not find version in pyproject.toml")
        sys.exit(1)
    
    major, minor, patch = map(int, match.groups())
    
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f'{major}.{minor}.{patch}'
    new_content = re.sub(version_pattern, f'version = "{new_version}"', content)
    write_pyproject(new_content)
    
    return new_version

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['major', 'minor', 'patch']:
        print("Usage: python bump_version.py [major|minor|patch]")
        sys.exit(1)
    
    version_type = sys.argv[1]
    new_version = bump_version(version_type)
    print(f"Version bumped to {new_version}")
    print(f"\nTo create a new release, run:")
    print(f"git add pyproject.toml")
    print(f"git commit -m 'Bump version to {new_version}'")
    print(f"git tag -a v{new_version} -m 'Release v{new_version}'")
    print(f"git push origin main --tags")

if __name__ == '__main__':
    main() 