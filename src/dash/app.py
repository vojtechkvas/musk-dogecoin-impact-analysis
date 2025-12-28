"""
Dash application initialization module.
This module configures the Dash app instance, themes, and multi-page routing.
"""

import dash_bootstrap_components as dbc
from dash_bootstrap_components.themes import BOOTSTRAP

from dash import Dash
from src.dash import router

external_stylesheets = [BOOTSTRAP]
external_stylesheets = [BOOTSTRAP, dbc.themes.CYBORG, dbc.icons.FONT_AWESOME]

app = Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
)

server = app.server


app.layout = router.layout()

from src.dash.pages.callbacks import callbacks
