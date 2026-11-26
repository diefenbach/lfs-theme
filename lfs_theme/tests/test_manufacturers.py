"""Manufacturer list: German labels, title, description and Open Graph."""

import re

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils import translation

from lfs_theme.tests.test_category_page import BASE, head_meta
from lfs_theme.tests.test_product_images import png
from lfs_theme.tests.test_titles import title_and_og

from lfs.catalog.models import Product
from lfs.manufacturer.models import Manufacturer


@pytest.fixture
def manufacturer(db):
    """A manufacturer with two active products."""
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    auma = Manufacturer.objects.create(name="auma", slug="auma")
    for slug in ("a", "b"):
        Product.objects.create(name=slug, slug=slug, active=True, price=1, manufacturer=auma)
    return auma


def test_product_count_is_labelled_products_in_german(client, manufacturer):
    with translation.override("de"):
        response = client.get(reverse("lfs_manufacturers"), HTTP_ACCEPT_LANGUAGE="de")
    html = " ".join(response.content.decode().split())
    assert "2 Produkte" in html
    assert "Monate" not in html


def test_list_has_its_own_title_description_and_open_graph(client, manufacturer):
    with translation.override("de"):
        title, og = title_and_og(client, reverse("lfs_manufacturers"))
        html = client.get(reverse("lfs_manufacturers")).content.decode()
    assert title == "Hersteller | LFS"
    assert og["og:title"] == "Hersteller"
    assert og["og:type"] == "website"
    assert '<meta name="description" content="Alle Hersteller und Marken bei LFS' in html


def test_manufacturer_page_has_title_and_type(client, manufacturer):
    response = client.get(reverse("lfs_manufacturer", kwargs={"slug": "auma"}))
    assert response.status_code == 200
    og = head_meta(response.content.decode())
    assert og["og:title"] == "auma"
    assert og["og:type"] == "website"


def test_manufacturer_image_is_used_for_open_graph(client, manufacturer, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    manufacturer.image.save("auma.png", png(600, 400))
    og = head_meta(client.get(reverse("lfs_manufacturer", kwargs={"slug": "auma"})).content.decode())
    assert re.fullmatch(rf"{BASE}/media/\S*auma\w*\.png", og["og:image"])
    assert (og["og:image:width"], og["og:image:height"]) == ("600", "400")


def test_list_leaves_out_manufacturers_without_active_products(client, manufacturer):
    remmers = Manufacturer.objects.create(name="Remmers", slug="remmers")
    Product.objects.create(name="Lasur", slug="lasur", active=False, price=1, manufacturer=remmers)
    Manufacturer.objects.create(name="menz", slug="menz")
    html = client.get(reverse("lfs_manufacturers")).content.decode()
    assert "/manufacturer-auma/" in html
    assert "/manufacturer-remmers/" not in html and "/manufacturer-menz/" not in html
