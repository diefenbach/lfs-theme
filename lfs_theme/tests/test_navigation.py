"""Category navigation: desktop menu, mobile menu, and footer come from one cached category tree, so a page needs
no category queries per category; the mobile menu is loaded on demand from its own URL."""

import re

import pytest
from django.core.cache import cache
from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from lfs.catalog.models import Category, Product

LOCMEM = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


@pytest.fixture
def shop(db):
    call_command("loaddata", "lfs_shop.xml", verbosity=0)


@pytest.fixture
def garden(shop):
    """Garden > Tools > Spades, plus a hidden category under Garden."""
    garden = Category.objects.create(name="Garden", slug="garden")
    tools = Category.objects.create(name="Tools", slug="tools", parent=garden)
    Category.objects.create(name="Spades", slug="spades", parent=tools)
    Category.objects.create(name="Hidden", slug="hidden", parent=garden, exclude_from_navigation=True)
    return garden


@pytest.fixture
def locmem(settings):
    settings.CACHES = LOCMEM
    cache.clear()
    yield
    cache.clear()


def drawer(html: str) -> str:
    """Return the opening tag of the mobile menu drawer."""
    return re.search(r'<nav class="mobile-nav-sidebar"[^>]*>', html).group(0)


def category_queries(path: str, client) -> int:
    """Return how many queries on the category table rendering ``path`` takes."""
    with CaptureQueriesContext(connection) as queries:
        client.get(path)
    return sum('"catalog_category"' in query["sql"] for query in queries.captured_queries)


def test_navigation_needs_the_same_queries_however_many_categories_there_are(client, garden):
    few = category_queries("/", client)
    for i in range(5):
        parent = Category.objects.create(name=f"Root {i}", slug=f"root-{i}")
        for j in range(3):
            Category.objects.create(name=f"Child {i}-{j}", slug=f"child-{i}-{j}", parent=parent)

    assert category_queries("/", client) == few


def test_cached_navigation_needs_no_category_queries(client, garden, locmem):
    client.get("/")

    assert category_queries("/", client) == 0


def test_desktop_menu_and_footer_show_two_levels_below_the_top_without_hidden_categories(client, garden):
    html = client.get("/").content.decode()

    nav = html[html.index('<nav class="desktop-nav"') : html.index('<nav class="mobile-nav-sidebar"')]
    assert re.search(r'class="desktop-nav-item-level-2" href="/category-tools/"', nav)
    assert re.search(r'class="desktop-nav-item-level-3" href="/category-spades/"', nav)
    footer = html[html.index('<nav class="categories-footer"') :]
    assert 'href="/category-garden/"' in footer and 'href="/category-tools/"' in footer
    assert "Hidden" not in nav and "Hidden" not in footer


def test_desktop_menu_marks_the_path_to_the_current_category(client, garden):
    html = client.get("/category-spades/").content.decode()

    assert re.search(r'class="desktop-nav-item active"[^>]*>\s*Garden', html)
    assert 'class="desktop-nav-item-level-2 active" href="/category-tools/"' in html
    assert 'class="desktop-nav-item-level-3 active" href="/category-spades/"' in html


def test_page_holds_only_an_empty_drawer_that_names_the_menu_url_and_the_current_category(client, garden):
    html = client.get("/category-tools/").content.decode()

    tag = drawer(html)
    assert 'data-src="/theme/mobile-menu/?v=' in tag
    assert 'data-current="/category-tools/"' in tag
    assert re.search(r'<nav class="mobile-nav-sidebar"[^>]*>\s*</nav>', html)


def test_drawer_on_a_product_page_names_the_products_category(client, garden):
    product = Product.objects.create(name="Spade", slug="spade", active=True)
    product.categories.add(Category.objects.get(slug="spades"))

    assert 'data-current="/category-spades/"' in drawer(client.get(product.get_absolute_url()).content.decode())


def test_mobile_menu_url_returns_all_levels_with_an_all_in_entry_and_no_hidden_categories(client, garden):
    src = re.search(r'data-src="([^"]+)"', client.get("/").content.decode()).group(1).replace("&amp;", "&")

    response = client.get(src)

    menu = response.content.decode()
    assert re.search(r'<button type="button" class="mobile-nav-link mobile-nav-sub-menu-link">\s*Garden', menu)
    assert re.search(r'<button type="button" class="mobile-nav-link mobile-nav-sub-menu-link">\s*Tools', menu)
    assert re.search(r'<a class="mobile-nav-link" href="/category-spades/">\s*Spades', menu)
    assert re.search(r'href="/category-garden/">\s*All in Garden', menu)
    sub_menu = menu[menu.index('class="mobile-nav-items mobile-nav-sub-menu"') :]
    assert '<span class="mobile-nav-title">Garden</span>' in sub_menu
    assert 'class="mobile-nav-back-link"' in sub_menu and 'class="mobile-nav-close"' in sub_menu
    assert "Hidden" not in menu
    assert "max-age" in response["Cache-Control"]


def test_saving_a_category_updates_the_cached_menus_and_the_menu_url(client, garden, locmem):
    before = client.get("/").content.decode()
    tools = Category.objects.get(slug="tools")
    tools.name = "Garden tools"
    tools.save()

    after = client.get("/").content.decode()

    assert "Garden tools" in after
    assert re.search(r'data-src="([^"]+)"', after).group(1) != re.search(r'data-src="([^"]+)"', before).group(1)


def test_deleting_a_category_removes_it_from_the_cached_menus(client, garden, locmem):
    client.get("/")
    Category.objects.get(slug="spades").delete()

    assert "/category-spades/" not in client.get("/").content.decode()


@pytest.mark.urls("lfs_theme.tests.urls_without_theme")
def test_shop_without_the_theme_urls_gets_the_mobile_menu_inside_the_page(client, garden):
    html = client.get("/").content.decode()

    assert "data-src" not in drawer(html)
    assert re.search(r'class="mobile-nav-link mobile-nav-sub-menu-link">\s*Garden', html)
