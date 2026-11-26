"""Product variants in JSON-LD: a ProductGroup with all variants, linked from the shown variant."""

import json
import re

import pytest
from django.core.management import call_command
from django.urls import reverse

from lfs.core.templatetags.lfs_seo_tags import variant_aspect
from lfs.catalog.models import Product, ProductPropertyValue, Property, PropertyGroup, PropertyOption
from lfs.catalog.settings import (
    PRODUCT_WITH_VARIANTS,
    PROPERTY_SELECT_FIELD,
    PROPERTY_VALUE_TYPE_VARIANT,
    VARIANT,
)

BASE = "https://testserver"


@pytest.fixture
def parent(db):
    """A deck board with two length variants; the first is the default."""
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    parent = Product.objects.create(
        name="Decking board", slug="decking-board", sku="07-006", active=True, price=20,
        sub_type=PRODUCT_WITH_VARIANTS,
    )
    length = Property.objects.create(name="Länge amerikanisch", title="Länge", type=PROPERTY_SELECT_FIELD,
                                     variants=True)
    group = PropertyGroup.objects.create(name="amerikanische Längen")
    group.products.add(parent)
    for position, (slug, value, price) in enumerate([("decking-board-215-m", "2,15 m", 22.23),
                                                     ("decking-board-244-m", "2,44 m", 25.10)]):
        option = PropertyOption.objects.create(property=length, name=value)
        variant = Product.objects.create(
            slug=slug, sub_type=VARIANT, parent=parent, active=True, variant_position=position,
            active_price=True, price=price, sku="07-006-244" if position else "", active_sku=bool(position),
        )
        ProductPropertyValue.objects.create(product=variant, property=length, property_group=group,
                                            value=str(option.id), type=PROPERTY_VALUE_TYPE_VARIANT)
    parent.default_variant = Product.objects.get(slug="decking-board-215-m")
    parent.save()
    return parent


def json_ld(client, slug):
    """Render a product page and return its JSON-LD blocks by type."""
    response = client.get(reverse("lfs_product", kwargs={"slug": slug}))
    assert response.status_code == 200
    blocks = [json.loads(block) for block in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', response.content.decode(), re.S)]
    return {block["@type"]: block for block in blocks}


def test_variant_page_has_a_product_group_with_all_variants(client, parent):
    group = json_ld(client, "decking-board-215-m")["ProductGroup"]
    assert group["@id"] == f"{BASE}/product/decking-board/#group"
    assert group["name"] == "Decking board"
    assert group["url"] == f"{BASE}/product/decking-board/"
    assert group["productGroupID"] == "07-006"
    assert group["variesBy"] == ["https://schema.org/size"]
    shown, other = group["hasVariant"]
    assert shown == {"@id": f"{BASE}/product/decking-board-215-m/#product", "size": "2,15 m"}
    assert other["@id"] == f"{BASE}/product/decking-board-244-m/#product"
    assert other["name"] == "Decking board – Länge 2,44 m"
    assert other["url"] == f"{BASE}/product/decking-board-244-m/"
    assert other["sku"] == "07-006-244"
    assert other["size"] == "2,44 m"
    assert other["offers"]["price"] == "25.10"
    assert other["offers"]["url"] == f"{BASE}/product/decking-board-244-m/"


def test_shown_variant_is_linked_to_its_group_and_named_by_its_properties(client, parent):
    product = json_ld(client, "decking-board-215-m")["Product"]
    assert product["@id"] == f"{BASE}/product/decking-board-215-m/#product"
    assert product["name"] == "Decking board – Länge 2,15 m"
    assert product["isVariantOf"] == {"@id": f"{BASE}/product/decking-board/#group"}


def test_variants_without_their_own_sku_get_none(client, parent):
    """LFS variants inherit the parent's SKU, which is the group ID; a variant's sku must identify it."""
    assert "sku" not in json_ld(client, "decking-board-215-m")["Product"]
    assert json_ld(client, "decking-board-244-m")["Product"]["sku"] == "07-006-244"
    shown, _ = json_ld(client, "decking-board-244-m")["ProductGroup"]["hasVariant"]
    assert "sku" not in shown


def test_parent_page_shows_the_same_group_with_the_default_variant(client, parent):
    blocks = json_ld(client, "decking-board")
    assert blocks["ProductGroup"]["url"] == f"{BASE}/product/decking-board/"
    assert blocks["Product"]["@id"] == f"{BASE}/product/decking-board-215-m/#product"


def test_product_without_variants_has_no_group(client, parent):
    Product.objects.create(name="Pfostenschraube", slug="schraube", active=True, price=1)
    blocks = json_ld(client, "schraube")
    assert "ProductGroup" not in blocks
    assert "isVariantOf" not in blocks["Product"]
    assert blocks["Product"]["name"] == "Pfostenschraube"


def test_product_without_variants_keeps_its_sku(client, parent):
    Product.objects.create(name="Pfostenschraube", slug="schraube", sku="12-345", active=True, price=1)
    assert json_ld(client, "schraube")["Product"]["sku"] == "12-345"


@pytest.mark.parametrize(("title", "aspect"), [
    ("Länge", "size"), ("Zaunhöhe", "size"), ("Scheerer Marwede Größe", "size"), ("Farbe", "color"),
    ("Scheerer Lasur + unbehandelt 2022", "color"), ("Holzart", "material"), ("DIN Richtung", None),
    ("Befestigung", None),
])
def test_variant_aspect_maps_property_titles_to_schema_org(title, aspect):
    assert variant_aspect(title) == aspect


def test_all_offers_have_the_return_policy_of_the_shop(client, parent):
    from lfs.core.utils import get_default_shop

    shop = get_default_shop()
    shop.return_policy_url = "/page/widerrufsbelehrung/"
    shop.save()
    blocks = json_ld(client, "decking-board-215-m")
    policy = blocks["Product"]["offers"]["hasMerchantReturnPolicy"]
    assert policy["@type"] == "MerchantReturnPolicy"
    assert policy["merchantReturnDays"] == 14
    assert policy["refundType"] == "https://schema.org/FullRefund"
    assert policy["merchantReturnLink"] == f"{BASE}/page/widerrufsbelehrung/"
    _, other = blocks["ProductGroup"]["hasVariant"]
    assert other["offers"]["hasMerchantReturnPolicy"] == policy
