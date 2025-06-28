#!/usr/bin/env python3
"""
Just De Pic - Image Metadata Removal and Editing Tool
Entry point that handles virtual environment setup and launches the application.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_and_setup_venv():
    """Check if venv exists, create if needed, and install dependencies."""
    venv_path = Path("venv")
    
    # Check if we're already in a virtual environment
    if sys.prefix == sys.base_prefix and not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Determine the correct python executable in the venv
        if platform.system() == "Windows":
            python_executable = venv_path / "Scripts" / "python.exe"
            pip_executable = venv_path / "Scripts" / "pip.exe"
        else:
            python_executable = venv_path / "bin" / "python"
            pip_executable = venv_path / "bin" / "pip"
        
        # Install requirements
        print("Installing dependencies...")
        subprocess.run([str(pip_executable), "install", "-r", "requirements.txt"], check=True)
        
        # Restart the script with the venv python
        print("Restarting with virtual environment...")
        os.execv(str(python_executable), [str(python_executable)] + sys.argv)
    
    # If we're in venv or venv exists, check if packages are installed
    try:
        import PIL
        import piexif
    except ImportError:
        print("Installing missing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)


def main():
    """Main entry point for the application."""
    check_and_setup_venv()
    
    # Import and run the GUI
    from gui.main_window import JustDePicApp
    
    app = JustDePicApp()
    app.run()


if __name__ == "__main__":
    main()