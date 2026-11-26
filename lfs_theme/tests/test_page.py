"""Information pages (AGB, Impressum, ...): Open Graph tags."""

import pytest
from django.core.management import call_command
from django.urls import reverse

from lfs_theme.tests.test_category_page import head_meta
from lfs.page.models import Page


@pytest.fixture
def page(db):
    """An active terms page whose meta title uses the page title."""
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    if not Page.objects.filter(pk=1).exists():
        Page.objects.create(pk=1, title="Root", slug="root")  # LFS serves no page with id 1
    return Page.objects.create(title="Terms", slug="terms", active=True, meta_title="<title>")


def test_page_has_title_type_and_the_share_card(client, page):
    response = client.get(reverse("lfs_page_view", kwargs={"slug": "terms"}))
    assert response.status_code == 200
    og = head_meta(response.content.decode())
    assert og["og:title"] == "Terms"
    assert og["og:type"] == "website"
