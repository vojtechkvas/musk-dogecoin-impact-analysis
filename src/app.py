# File: src/app.py (inside the src/ directory)

from dash import Dash
from dash_bootstrap_components.themes import BOOTSTRAP # Example of an external stylesheet

import dash_bootstrap_components as dbc

# Define external stylesheets (useful for professional design)
# Common options: BOOTSTRAP, CERULEAN, MINTY, etc.
external_stylesheets = [BOOTSTRAP] 
external_stylesheets=[BOOTSTRAP, dbc.themes.CYBORG, dbc.icons.FONT_AWESOME]
# Initialize the Dash app
# - __name__ is important for locating static assets and callbacks.
# - suppress_callback_exceptions=True is needed for multi-page apps
#   where not all components exist on every page simultaneously.
app = Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    # Add other configurations here, like title, update interval, etc.
)

# Optional: Define the underlying Flask server instance
# You can use app.server to interact with Flask features directly.
server = app.server

# -----------------------------------------------------------------
# IMPORTANT: Import the layout and register callbacks AFTER initialization
# This prevents circular import issues and ensures all definitions are loaded.
# -----------------------------------------------------------------

from src import layout # Imports the layout defined in src/layout.py
from src import callbacks # Imports callback functions defined in src/callbacks.py

# Assign the main layout
app.layout = layout.main_layout