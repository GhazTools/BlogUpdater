"""
file_name = blueprints.py
Created On: 2024/07/10
Lasted Updated: 2024/07/10
Description: _FILL OUT HERE_
Edit Log:
2024/07/10
    - Created file
"""

# STANDARD LIBRARY IMPORTS

# THIRD PARTY LIBRARY IMPORTS
from sanic import Blueprint
from sanic.request import Request
from sanic.response import text, HTTPResponse

# LOCAL LIBRARY IMPORTS


ENTRY_POINT_BLUEPRINT = Blueprint("entry_point_blueprint", url_prefix="/")


@ENTRY_POINT_BLUEPRINT.get("/")
async def entry_point(request: Request) -> HTTPResponse:  # pylint: disable=unused-argument
    """
    A request to validate that the app is running
    """

    return text("App is currently running.")


BLUEPRINTS: list[Blueprint] = [ENTRY_POINT_BLUEPRINT]
