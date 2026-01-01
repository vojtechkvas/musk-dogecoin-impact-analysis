"""
Main Application Layout Module.

This module defines the top-level structure of the Dash application, including
the navigation bar and the main content container that hosts the multi-page
content. It uses Dash Bootstrap Components for a responsive design and
'dash.page_container' to manage page routing.
"""

import dash
import dash_bootstrap_components as dbc


def layout() -> dbc.Container:
    """
    Constructs the top-level UI structure for the Dash application.

    This function defines a responsive Bootstrap container that houses the
    global navigation bar and a dynamic content area. The navigation bar
    includes links to the 'Home' and 'Deep Analysis' pages, while
    'dash.page_container' serves as the anchor for multi-page routing.

    Returns:
        dbc.Container: A Dash Bootstrap Components Container object
                       representing the root layout of the app.
    """
    return dbc.Container(
        [
            dbc.NavbarSimple(
                children=[
                    dbc.NavItem(
                        dbc.NavLink(
                            "Home",
                            href="/",
                            active="exact",
                            className="fs-5 mx-2",
                        )
                    ),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Deep Analysis",
                            href="/analysis",
                            active="exact",
                            className="fs-5 mx-2",
                        )
                    ),
                ],
                brand="DOGE Tracker",
                brand_style={"fontSize": "2.5rem", "fontWeight": "bold"},
                color="primary",
                dark=True,
                className="fs-3",
            ),
            dash.page_container,
        ],
        fluid=True,
    )
