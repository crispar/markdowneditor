#!/usr/bin/env python3
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.app import create_app


def main():
    app = create_app()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
