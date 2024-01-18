from django.core.cache import cache
from django.template import Library, Node, TemplateSyntaxError
from django.utils.translation import gettext as _

from portlets.models import Slot

from lfs.catalog.models import Category
import lfs.core.utils

register = Library()


class SlotsInformationNode(Node):
    """ """

    def render(self, context):
        request = context.get("request")
        obj = context.get("category") or context.get("product") or context.get("page")
        if obj is None or obj.__class__.__name__.lower() not in ("category", "product", "page"):
            obj = lfs.core.utils.get_default_shop(request)

        slots = cache.get("slots")
        if slots is None:
            slots = Slot.objects.all()
            cache.set("slots", slots)

        for slot in slots:
            cache_key = "has-portlets-%s-%s-%s" % (obj.__class__.__name__, obj.id, slot.name)
            has_portlets = cache.get(cache_key)
            if has_portlets is None:
                has_portlets = slot.has_portlets(obj)
                cache.set(cache_key, has_portlets)

            context["Slot%s" % slot.name] = has_portlets

        cache_key = "content-class-%s-%s" % (obj.__class__.__name__, obj.id)
        content_class = cache.get(cache_key)
        if content_class is None:
            content_class = "col-12"
            if context.get("SlotLeft", None) and context.get("SlotRight", None):
                content_class = "col-8"
            elif context.get("SlotLeft", None):
                content_class = "col-10"
            elif context.get("SlotRight", None):
                content_class = "col-10"

            cache.set(cache_key, content_class)

        context["content_class"] = content_class
        return ""


def do_slots_information(parser, token):
    """Calculates some context variables based on displayed slots."""
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 1:
        raise TemplateSyntaxError(_("%s tag needs no argument") % bits[0])

    return SlotsInformationNode()


register.tag("slots_information", do_slots_information)


@register.inclusion_tag("lfs/mail/mail_html_footer.html", takes_context=True)
def email_html_footer(context):
    request = context.get("request", None)
    shop = lfs.core.utils.get_default_shop(request)
    return {"shop": shop}


@register.inclusion_tag("lfs/mail/mail_text_footer.html", takes_context=True)
def email_text_footer(context):
    request = context.get("request", None)
    shop = lfs.core.utils.get_default_shop(request)
    return {"shop": shop}


@register.inclusion_tag("lfs_theme/menu/top_nav.html", takes_context=True)
def top_nav(context):
    """Renders the top navigation.

    In this case it is all top categories with their children up to level 3.
    """
    request = context.get("request")
    obj = context.get("product") or context.get("category")

    categories = []
    current_top_category = lfs.catalog.utils.get_current_top_category(request, obj)
    for category_level_1 in Category.objects.filter(parent=None):
        if category_level_1.exclude_from_navigation:
            continue

        if current_top_category:
            current = current_top_category.id == category_level_1.id
        else:
            current = False

        categories_level_2 = []
        for category_level_2 in category_level_1.get_children().filter(exclude_from_navigation=False):
            if category_level_2.exclude_from_navigation:
                continue

            categories_level_3 = []
            for category_level_3 in category_level_2.get_children():
                if category_level_3.exclude_from_navigation:
                    continue

                categories_level_3.append(
                    {
                        "name": category_level_3.name,
                        "url": category_level_3.get_absolute_url(),
                    }
                )

            categories_level_2.append(
                {
                    "name": category_level_2.name,
                    "url": category_level_2.get_absolute_url(),
                    "children": categories_level_3,
                    "image": category_level_2.get_image(),
                }
            )

        categories.append(
            {
                "name": category_level_1.name,
                "url": category_level_1.get_absolute_url(),
                "children": categories_level_2,
                "current": current,
            }
        )

    return {
        "categories": categories,
    }


@register.inclusion_tag("lfs_theme/menu/sidebar_nav.html", takes_context=True)
def sidebar_nav(context):
    ct = lfs.core.utils.CategoryTree(currents=[], start_level=1, expand_level=100)
    return {"category_tree": ct.get_category_tree()}


@register.inclusion_tag("lfs_theme/menu/sidebar_nav_children.html", takes_context=True)
def sidebar_nav_children(context, category):
    return {
        "category": category["category"],
        "categories": category["children"],
    }
