"""Contact form: title, description and Open Graph."""

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils import translation

from lfs_theme.tests.test_titles import title_and_og


@pytest.fixture
def shop(db):
    """The default shop."""
    call_command("loaddata", "lfs_shop.xml", verbosity=0)


def test_contact_has_a_description_and_open_graph(client, shop):
    with translation.override("de"):
        title, og = title_and_og(client, reverse("lfs_contact_form"))
        html = client.get(reverse("lfs_contact_form")).content.decode()
    assert title == "Kontaktformular | LFS"
    assert og["og:title"] == "Kontaktformular"
    assert og["og:type"] == "website"
    assert '<meta name="description" content="Fragen? Schreiben Sie uns' in html
