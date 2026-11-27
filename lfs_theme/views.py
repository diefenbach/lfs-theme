"""Views of the theme."""

from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from lfs_theme.navigation import get_category_tree


@require_GET
@cache_control(public=True, max_age=86400)
def mobile_menu(request: HttpRequest) -> HttpResponse:
    """Return the levels of the mobile menu, which main.js loads into the drawer when it is first opened.

    The menu is the same on every page (main.js marks the current category), so browsers may keep it: pages link it
    with the tree's version, which changes with every change of the categories.
    """
    html = render_to_string("lfs_theme/mobile_menu.html", {"categories": get_category_tree()["categories"]})
    return HttpResponse(html)
