"""Page titles: the page's own meta title plus a short site name, and og:site_name."""

import re

from django.urls import reverse
from django.utils import translation

from lfs_theme.tests.test_category_page import categories, head_meta  # noqa: F401 (fixture)
from lfs_theme.tests.test_page import page  # noqa: F401 (fixture)


# The shop name from the core fixture lfs_shop.xml, which the theme appends to page titles.
SITE_NAME = "LFS"


def title_and_og(client, url):
    """Return the page's <title> text (whitespace collapsed) and its og:* tags."""
    response = client.get(url)
    assert response.status_code == 200
    html = response.content.decode()
    title = " ".join(re.search(r"<title>(.*?)</title>", html, re.S).group(1).split())
    return title, head_meta(html)


def test_category_title_is_its_meta_title_and_the_site_name(client, categories):
    title, og = title_and_og(client, reverse("lfs_category", kwargs={"slug": "terraces"}))
    assert title == f"Wooden terraces | {SITE_NAME}"
    assert og["og:site_name"] == SITE_NAME


def test_product_title_is_its_meta_title_and_the_site_name(client, categories):
    title, og = title_and_og(client, reverse("lfs_product", kwargs={"slug": "decking-board"}))
    assert title == f"Decking board | {SITE_NAME}"
    assert og["og:title"] == "Decking board"


def test_page_title_is_its_meta_title_and_the_site_name(client, page):
    title, _ = title_and_og(client, reverse("lfs_page_view", kwargs={"slug": "terms"}))
    assert title == f"Terms | {SITE_NAME}"


def test_homepage_keeps_the_shop_meta_title(client, categories):
    from lfs.core.models import Shop

    Shop.objects.filter(pk=1).update(meta_title="Welcome to our shop")
    title, og = title_and_og(client, reverse("lfs_shop_view"))
    assert title == "Welcome to our shop"
    assert og["og:site_name"] == SITE_NAME


def test_category_title_names_the_page_only_from_page_two(client, categories):
    from lfs.catalog.models import Product

    for number in range(10):
        product = Product.objects.create(name=f"Board {number}", slug=f"board-{number}", active=True, price=1)
        categories.products.add(product)
    url = reverse("lfs_category", kwargs={"slug": "terraces"})
    with translation.override("de"):
        assert title_and_og(client, url)[0] == f"Wooden terraces | {SITE_NAME}"
        assert title_and_og(client, f"{url}?start=2")[0] == f"Wooden terraces - Seite 2 | {SITE_NAME}"
