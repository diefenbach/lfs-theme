"""Category page: Open Graph tags and sizes of the product images."""

import re

import pytest
from django.core.management import call_command
from django.urls import reverse

from lfs_theme.tests.test_product_images import png
from lfs.catalog.models import Category, Image, Product
from lfs.core.models import Shop

BASE = "http://testserver"


@pytest.fixture
def categories(db, settings, tmp_path):
    """A category with an image and a product, and a subcategory-free one without an image."""
    settings.MEDIA_ROOT = tmp_path
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    terraces = Category.objects.create(name="Terraces", slug="terraces", meta_title="Wooden terraces")
    terraces.image.save("terraces.png", png(1200, 800))
    product = Product.objects.create(name="Decking board", slug="decking-board", active=True, price=10)
    Image(content=product, title="Decking.jpg", position=0).image.save("decking.png", png(800, 600))
    terraces.products.add(product)
    Category.objects.create(name="Fences", slug="fences")
    return terraces


def head_meta(html):
    """Return the og:* meta tags of a page as a dict."""
    return dict(re.findall(r'<meta property="(og:[a-z_:]+)" content="([^"]*)"', html))


def render(client, slug):
    response = client.get(reverse("lfs_category", kwargs={"slug": slug}))
    assert response.status_code == 200
    return response.content.decode()


def test_category_has_title_type_and_its_image_for_open_graph(client, categories):
    og = head_meta(render(client, "terraces"))
    assert og["og:title"] == "Wooden terraces"
    assert og["og:type"] == "website"
    assert re.fullmatch(rf"{BASE}/media/images/terraces\w*\.png", og["og:image"])
    assert (og["og:image:width"], og["og:image:height"]) == ("1200", "800")


def test_category_without_image_uses_the_shop_image(client, categories):
    shop = Shop.objects.get()
    shop.image.save("shop.png", png(1200, 630))
    og = head_meta(render(client, "fences"))
    assert og["og:title"] == "Fences"
    assert re.fullmatch(rf"{BASE}/media/\S*shop\w*\.png", og["og:image"])
    assert (og["og:image:width"], og["og:image:height"]) == ("1200", "630")


def test_category_without_image_has_no_og_image_when_the_shop_has_none(client, categories):
    assert "og:image" not in head_meta(render(client, "fences"))


def test_product_tiles_have_the_real_thumbnail_size(client, categories):
    html = render(client, "terraces")
    tile = re.search(r'<div class="product-image[^"]*">\s*(<img[^>]*>)', html).group(1)
    assert 'width="200"' in tile and 'height="150"' in tile
    assert 'alt="Decking board"' in tile
