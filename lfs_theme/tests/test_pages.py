"""Every storefront page renders with the theme, also with a filled cart (search needs PostgreSQL and is left out)."""

import pytest
from django.urls import reverse

from lfs_theme.tests.test_category_page import categories  # noqa: F401 (fixture)

PAGES = [
    "/", "/category-terraces/", "/product/decking-board/", "/cart/", "/contact", "/manufacturers/", "/login/",
    "/checkout-login/", "/checkout/addresses", "/checkout/payment-and-shipping", "/checkout/check-and-pay",
    "/thank-you/", "/robots.txt", "/password-reset/",
]


@pytest.mark.parametrize("url", PAGES)
def test_page_renders_with_a_filled_cart(client, categories, url):
    from lfs.catalog.models import Product

    product = Product.objects.get(slug="decking-board")
    client.post(reverse("lfs_add_to_cart"), {"product_id": product.id, "quantity": "2", "action": "add-to-cart"})
    response = client.get(url, follow=True)
    assert response.status_code == 200
