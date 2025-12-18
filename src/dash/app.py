from dash import Dash
from dash_bootstrap_components.themes import BOOTSTRAP

import dash_bootstrap_components as dbc
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


from src.dash.pages.callbacks import callbacks


# #  app.layout = layout.main_layout
app.layout = router.layout()
