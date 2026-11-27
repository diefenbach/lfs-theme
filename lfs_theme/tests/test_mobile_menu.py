"""Mobile category menu: a drawer from the left with a header row (back, title, close), an "All in <category>"
entry per level, and the current category path marked so the menu can open where the visitor is."""

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


def test_sub_menu_has_a_header_row_and_an_all_in_entry(client, garden):
    menu = drawer(client.get(reverse("lfs_shop_view")).content.decode())

    sub_menu = menu[menu.index('class="mobile-nav-items mobile-nav-sub-menu"') :]
    assert '<span class="mobile-nav-title">Garden</span>' in sub_menu
    assert 'class="mobile-nav-back-link"' in sub_menu and 'class="mobile-nav-close"' in sub_menu
    assert f'href="{garden.get_absolute_url()}"' in sub_menu and "All in Garden" in sub_menu
    assert "Show Garden" not in menu


def test_current_category_path_is_marked_for_opening_the_menu_there(client, garden):
    tools = Category.objects.get(slug="tools")

    menu = drawer(client.get(tools.get_absolute_url()).content.decode())

    assert re.search(r'<li class="mobile-nav-item mobile-nav-expand is-current">\s*<button[^>]*>\s*Garden', menu)
    assert re.search(rf'<a class="mobile-nav-link" href="{tools.get_absolute_url()}" aria-current="page">', menu)
