import sys
import os

# Add src folder to module search path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.console import start_console

if __name__ == "__main__":
    start_console()
