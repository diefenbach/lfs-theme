"""Header and footer: shop name, cart badge, and footer links from the shop's Footer actions."""

import pytest
from django.core.management import call_command
from django.urls import reverse

from lfs.core.models import Action, ActionGroup


@pytest.fixture
def shop(db):
    call_command("loaddata", "lfs_shop.xml", verbosity=0)


def test_header_shows_the_shop_name_without_a_logo(client, shop):
    html = client.get(reverse("lfs_shop_view")).content.decode()
    assert '<span class="shop-name">LFS</span>' in html


def test_cart_badge_is_hidden_while_the_cart_is_empty(client, shop):
    html = client.get(reverse("lfs_shop_view")).content.decode()
    assert '<span class="badge rounded-pill bg-danger cart-items-count" hidden>' in html


def test_footer_links_come_from_the_footer_actions(client, shop):
    group, _ = ActionGroup.objects.get_or_create(name="Footer")
    Action.objects.create(group=group, title="Imprint", link="/page/imprint/", active=True, position=1)
    html = client.get(reverse("lfs_shop_view")).content.decode()
    assert '<a href="/page/imprint/">Imprint</a>' in html
    assert "/page/agb" not in html and "/page/datenschutz" not in html


def _account_menu(html: str) -> str:
    """Return the markup of the account menu behind the person icon."""
    start = html.index('<div class="dropdown account-menu">')
    return html[start : html.index("</ul>", start)]


def test_account_menu_holds_my_account_manage_and_logout_for_a_superuser(admin_client, shop):
    html = admin_client.get(reverse("lfs_shop_view")).content.decode()

    menu = _account_menu(html)
    for name in ("lfs_my_account", "lfs_manage_dashboard", "lfs_logout"):
        assert f'href="{reverse(name)}"' in menu
    assert 'class="management"' not in html


def test_account_menu_has_no_manage_link_for_a_customer(client, django_user_model, shop):
    client.force_login(django_user_model.objects.create_user("joe", "joe@example.com", "secret"))

    menu = _account_menu(client.get(reverse("lfs_shop_view")).content.decode())

    assert f'href="{reverse("lfs_logout")}"' in menu
    assert reverse("lfs_manage_dashboard") not in menu


def test_mobile_menu_button_sits_next_to_the_cart(client, shop):
    html = client.get(reverse("lfs_shop_view")).content.decode()

    actions = html[html.index('<div class="header-actions">') :]
    actions = actions[: actions.index("</div>")]
    assert actions.index('class="cart-link"') < actions.index('class="mobile-nav-toggle-btn"')
    assert html.count('class="mobile-nav-toggle-btn"') == 1
