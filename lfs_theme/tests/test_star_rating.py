"""Star ratings are drawn with Bootstrap Icons: full, half, and empty stars for a score, and a review form whose
stars set the score."""

import re

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.template import Context, Template
from django.urls import reverse

from lfs.catalog.models import Product
from reviews.models import Review


def stars(html: str) -> list[str]:
    """Return the kind of every star icon in ``html``: "fill", "half", or "empty"."""
    kinds = {"bi-star-fill": "fill", "bi-star-half": "half", "bi-star": "empty"}
    return [kinds[name] for name in re.findall(r'class="bi (bi-star(?:-fill|-half)?)"', html)]


def render(score: object) -> str:
    """Render the star_rating tag for ``score``."""
    return Template("{% load lfs_theme_tags %}{% star_rating score %}").render(Context({"score": score}))


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (5, ["fill"] * 5),
        (3.5, ["fill"] * 3 + ["half", "empty"]),
        (3.3, ["fill"] * 3 + ["half", "empty"]),
        (3.2, ["fill"] * 3 + ["empty"] * 2),
        (0, ["empty"] * 5),
        (None, ["empty"] * 5),
    ],
)
def test_score_is_drawn_with_full_half_and_empty_stars(score, expected):
    assert stars(render(score)) == expected


def test_stars_tell_screen_readers_the_score():
    assert 'aria-label="3.5 of 5 stars"' in render(3.5)


@pytest.fixture
def product(db):
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    return Product.objects.create(name="Spade", slug="spade", active=True)


def test_review_form_offers_five_star_buttons_that_set_the_score(client, product):
    content_type = ContentType.objects.get_for_model(Product)
    html = client.get(reverse("reviews_add", args=[content_type.id, product.id])).content.decode()

    buttons = re.findall(r'<button type="button" class="rate" data-score="([^"]+)"', html)
    assert buttons == ["1.0", "2.0", "3.0", "4.0", "5.0"]
    assert "star.png" not in html and "current-rating" not in html


def test_score_of_a_star_button_is_accepted_by_the_review_form(client, product):
    """rating.js copies a button's data-score into the score field; the form must accept that value."""
    content_type = ContentType.objects.get_for_model(Product)
    url = reverse("reviews_add", args=[content_type.id, product.id])
    score = re.findall(r'data-score="([^"]+)"', client.get(url).content.decode())[3]

    client.post(url, {
        "score": score, "comment": "Good spade", "user_name": "Joe", "user_email": "joe@example.com",
        "content_type_id": content_type.id, "content_id": product.id,
    })

    assert Review.objects.get().score == 4.0


def _add_review(client, product, **data) -> None:
    """Post the review form for ``product`` with ``data``."""
    content_type = ContentType.objects.get_for_model(Product)
    client.post(reverse("reviews_add", args=[content_type.id, product.id]), {
        "score": "5.0", "comment": "Fine", "content_type_id": content_type.id, "content_id": product.id, **data,
    })


def test_logged_in_customer_without_full_name_is_shown_with_the_name_they_entered(client, django_user_model, product):
    """Customers log in with their e-mail and often have no first and last name on their user."""
    client.force_login(django_user_model.objects.create_user("kai", "kai@example.com", "secret"))
    form = client.get(reverse("reviews_add", args=[ContentType.objects.get_for_model(Product).id, product.id]))
    assert 'name="user_name"' in form.content.decode()

    _add_review(client, product, user_name="Kai")

    html = client.get(product.get_absolute_url()).content.decode()
    assert "Kai" in html and "Anonymous" not in html


def test_reviews_do_not_publish_the_reviewers_email(client, product):
    _add_review(client, product, user_name="Joe", user_email="joe@example.com")

    html = client.get(product.get_absolute_url()).content.decode()
    assert "Joe" in html
    assert "joe@example.com" not in html
