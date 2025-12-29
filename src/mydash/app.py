"""
Dash application initialization module.
This module configures the Dash app instance, themes, and multi-page routing.
"""

import dash_bootstrap_components as dbc

from dash import Dash
from src.mydash import router
from src.mydash.pages.callbacks import callbacks

external_stylesheets = [dbc.themes.CYBORG, dbc.icons.FONT_AWESOME]

app = Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
)

server = app.server


app.layout = router.layout()
