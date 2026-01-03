"""
Entry point for the Dash web application.

This script initializes and runs the Dash server. It imports the app instance
from the modular layout structure and starts the development server on a
specified port.
"""

from src.mydash.app import app

if __name__ == "__main__":
    app.run(debug=False, port=8050)
