"""
Main Application Layout Module.

This module defines the top-level structure of the Dash application, including
the navigation bar and the main content container that hosts the multi-page
content. It uses Dash Bootstrap Components for a responsive design and
'dash.page_container' to manage page routing.
"""

import dash_bootstrap_components as dbc

import dash


def layout():
    return dbc.Container(
        [
            dbc.NavbarSimple(
                children=[
                    dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
                    dbc.NavItem(
                        dbc.NavLink("Deep Analysis", href="/analysis", active="exact")
                    ),
                ],
                brand="DOGE Tracker",
                color="primary",
                dark=True,
            ),
            dash.page_container,
        ],
        fluid=True,
    )
