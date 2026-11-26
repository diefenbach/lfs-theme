"""Home page: structured data about the business that runs the shop (Organization / OnlineStore)."""

import json
import re

from django.urls import reverse

from lfs.core.models import Shop
from lfs_theme.tests.test_category_page import categories  # noqa: F401 (fixture)
from lfs_theme.tests.test_product_images import png


def home_json_ld(client):
    """Return the home page's JSON-LD entities by type, including those in an @graph."""
    html = client.get(reverse("lfs_shop_view")).content.decode()
    blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
    return {node["@type"]: node for block in blocks for node in block.get("@graph", [block])}


def test_home_page_describes_the_online_store(client, categories):
    store = home_json_ld(client)["OnlineStore"]
    assert store["name"] == "John Doe"
    assert store["alternateName"] == "LFS"
    assert store["url"] == "https://testserver/"
    assert "logo" not in store
    assert "email" not in store


def test_home_page_gives_the_shop_logo_and_email_when_set(client, categories):
    shop = Shop.objects.get()
    shop.from_email = "shop@example.com"
    shop.image.save("logo.png", png(400, 100))
    store = home_json_ld(client)["OnlineStore"]
    assert store["email"] == "shop@example.com"
    assert re.fullmatch(r"http://testserver/media/\S*logo\w*\.png", store["logo"])


def test_home_page_names_the_website_and_its_publisher(client, categories):
    entities = home_json_ld(client)
    assert entities["WebSite"]["name"] == "LFS"
    assert entities["WebSite"]["publisher"] == {"@id": entities["OnlineStore"]["@id"]}
    assert "potentialAction" not in entities["WebSite"]
