"""Optional add-ons: their markup appears only when they are installed, and pages render without them."""

import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse


@pytest.fixture
def shop(db):
    call_command("loaddata", "lfs_shop.xml", verbosity=0)


def test_home_page_renders_without_any_optional_add_on(client, shop):
    html = client.get(reverse("lfs_shop_view")).content.decode()
    assert "lfs_cookie_consent" not in html
    assert "lfs_gtm" not in html
    assert "swiper" not in html


@pytest.mark.skipif(
    not __import__("importlib").util.find_spec("lfs_cookie_consent"), reason="needs the lfs_cookie_consent add-on"
)
def test_cookie_consent_is_included_when_installed(client, shop):
    with override_settings(INSTALLED_APPS=[*settings.INSTALLED_APPS, "lfs_cookie_consent"]):
        html = client.get(reverse("lfs_shop_view")).content.decode()
    assert "lfs_cookie_consent/lfs_cookie_consent.css" in html
    assert "lfs_cookie_consent/lfs_cookie_consent.js" in html
    assert 'class="cookie-settings-link"' in html
