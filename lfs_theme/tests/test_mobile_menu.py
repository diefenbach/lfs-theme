"""Mobile category menu: the menu button controls the drawer; its levels are tested in test_navigation."""

import re

import pytest
from django.core.management import call_command
from django.urls import reverse

from lfs.catalog.models import Category


@pytest.fixture
def garden(db):
    """Garden with the subcategory Tools."""
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    garden = Category.objects.create(name="Garden", slug="garden")
    Category.objects.create(name="Tools", slug="tools", parent=garden)
    return garden


def drawer(html: str) -> str:
    """Return the markup of the mobile menu drawer."""
    start = html.index('<nav class="mobile-nav-sidebar"')
    return html[start : html.index("</nav>", start)]


def test_menu_button_controls_the_drawer_and_reports_it_is_closed(client, garden):
    html = client.get(reverse("lfs_shop_view")).content.decode()

    button = re.search(r'<button type="button" class="mobile-nav-toggle-btn"[^>]*>', html).group(0)
    assert 'aria-controls="mobile-nav"' in button and 'aria-expanded="false"' in button
    assert 'id="mobile-nav"' in drawer(html)
