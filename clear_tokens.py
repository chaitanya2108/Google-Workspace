"""
Clear old token files to force re-authentication with new scopes
"""
import os
from pathlib import Path

# Get the directory
config_dir = Path('config/tokens')

if config_dir.exists():
    # Delete all token files
    for token_file in config_dir.glob('*.json'):
        print(f"Deleting: {token_file}")
        token_file.unlink()
    print("All token files cleared. Please re-authenticate.")
else:
    print("No tokens directory found.")

