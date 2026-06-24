"""
Dash application initialization module.
This module configures the Dash app instance, themes, and multi-page routing.
"""

import dash_bootstrap_components as dbc
import diskcache
from dash import Dash, DiskcacheManager


from src.mydash import router

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)


external_stylesheets = [dbc.themes.CYBORG, dbc.icons.FONT_AWESOME]

app = Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    background_callback_manager=background_callback_manager,
)

server = app.server


app.layout = router.layout()
