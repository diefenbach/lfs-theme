"""Product page images: real thumbnail sizes and alt texts."""

import io
from html.parser import HTMLParser

import pytest
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.urls import reverse
from PIL import Image as PILImage

from lfs.core.templatetags.lfs_seo_tags import thumbnail_size
from lfs.catalog.models import Image, Product

PRODUCT_NAME = "Decking board"


def png(width, height):
    """Return a PNG of the given size as uploadable content."""
    buffer = io.BytesIO()
    PILImage.new("RGB", (width, height)).save(buffer, "PNG")
    return ContentFile(buffer.getvalue())


class ImageCollector(HTMLParser):
    """Collects the attributes of the images in the main image box and the thumbnail row."""

    def __init__(self):
        super().__init__()
        self.box = None
        self.depth = 0
        self.images = {"main-image": [], "sub-images": []}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if self.box:
            if tag == "img":
                self.images[self.box].append(attributes)
            elif tag == "div":
                self.depth += 1
        elif tag == "div" and attributes.get("class") in self.images:
            self.box = attributes["class"]

    def handle_endtag(self, tag):
        if self.box and tag == "div":
            if self.depth:
                self.depth -= 1
            else:
                self.box = None


@pytest.fixture
def product(db, settings, tmp_path):
    """A product with a landscape, a portrait (with alt) and a square image."""
    settings.MEDIA_ROOT = tmp_path
    call_command("loaddata", "lfs_shop.xml", verbosity=0)
    product = Product.objects.create(name=PRODUCT_NAME, slug="decking-board", active=True, price=10)
    for position, (title, alt, size) in enumerate([
        ("Decking.jpg", "", (800, 600)),
        ("Decking-detail.jpg", "Decking detail", (600, 800)),
        ("glatt.jpg", "", (800, 800)),
    ]):
        image = Image(content=product, title=title, alt=alt, position=position)
        image.image.save(f"image-{position}.png", png(*size))
    return product


def page_images(client, product):
    """Render the product page and return its main image and thumbnails."""
    response = client.get(reverse("lfs_product", kwargs={"slug": product.slug}))
    assert response.status_code == 200
    collector = ImageCollector()
    collector.feed(response.content.decode())
    return collector.images["main-image"], collector.images["sub-images"]


def test_thumbnail_size_is_read_from_the_thumbnail_file(product):
    landscape, portrait, _ = product.get_images()
    assert thumbnail_size(landscape.image, "400x400") == (400, 300)
    assert thumbnail_size(portrait.image, "60x60") == (45, 60)


def test_thumbnail_size_without_image_or_thumbnail_file(product, tmp_path):
    landscape = product.get_images()[0]
    (tmp_path / "images" / "image-0.200x200.png").unlink()
    assert thumbnail_size(None, "60x60") is None
    assert thumbnail_size(landscape.image, "200x200") is None


def test_main_image_has_its_size_the_title_and_the_product_name_as_alt(client, product):
    (main,), _ = page_images(client, product)
    assert (main["width"], main["height"]) == ("400", "300")
    assert main["title"] == "Decking.jpg"
    assert main["alt"] == PRODUCT_NAME


def test_thumbnails_use_the_alt_field_else_the_product_name_with_their_number(client, product):
    _, thumbnails = page_images(client, product)
    assert [(t["alt"], t["title"], t["width"], t["height"]) for t in thumbnails] == [
        (PRODUCT_NAME, "Decking.jpg", "60", "45"),
        ("Decking detail", "Decking-detail.jpg", "45", "60"),
        (f"{PRODUCT_NAME} – Image 3", "glatt.jpg", "60", "60"),
    ]
