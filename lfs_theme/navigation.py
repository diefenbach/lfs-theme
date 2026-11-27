"""The category tree behind the theme's navigation: desktop menu, mobile menu, and footer.

It is built with one query and kept in Django's cache, so a page needs no category queries for its menus, however
large the catalog is. LFS clears the whole cache whenever a category is saved or deleted (lfs.caching.listeners), which
drops the tree too.
"""

import hashlib
import json
from typing import TypedDict

from django.core.cache import cache

from lfs.catalog.models import Category

CACHE_KEY = "lfs_theme:category-tree"


class NavCategory(TypedDict):
    """A category shown in the navigation, with its shown children."""

    id: int
    name: str
    url: str
    image: str | None  # URL of the 60x60 thumbnail of the category's image, or of the nearest parent's
    children: list["NavCategory"]


class CategoryTree(TypedDict):
    """The top-level categories, and a version that changes whenever the tree does."""

    categories: list[NavCategory]
    version: str


def get_category_tree() -> CategoryTree:
    """Return the tree of categories shown in the navigation, from the cache or built with one query.

    Categories excluded from the navigation are left out together with everything below them.
    """
    tree = cache.get(CACHE_KEY)
    if tree is None:
        tree = _build_category_tree()
        cache.set(CACHE_KEY, tree)
    return tree


def _build_category_tree() -> CategoryTree:
    """Build the category tree from all categories shown in the navigation, ordered by position."""
    children: dict[int | None, list[Category]] = {}
    for category in Category.objects.filter(exclude_from_navigation=False):
        children.setdefault(category.parent_id, []).append(category)

    def build(parent_id: int | None, parent_image: str | None) -> list[NavCategory]:
        nodes = []
        for category in children.get(parent_id, []):
            image = category.image.url_60x60 if category.image else parent_image
            nodes.append({
                "id": category.id,
                "name": category.name,
                "url": category.get_absolute_url(),
                "image": image,
                "children": build(category.id, image),
            })
        return nodes

    categories = build(None, None)
    version = hashlib.sha256(json.dumps(categories).encode()).hexdigest()[:12]
    return {"categories": categories, "version": version}


def get_path(categories: list[NavCategory], category_id: int | None) -> list[NavCategory]:
    """Return the categories from the top level down to the category ``category_id``; empty if it is not shown."""
    for category in categories:
        if category["id"] == category_id:
            return [category]
        path = get_path(category["children"], category_id)
        if path:
            return [category, *path]
    return []

