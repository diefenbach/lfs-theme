"""Template tags of the LFS default theme: navigation, footer, slots, optional add-ons, and mail footers."""

from typing import Any

from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.forms import boundfield
from django.template import Context, Library, Node, TemplateSyntaxError
from django.template.base import Parser, Token
from django.template.loader import get_template, render_to_string
from django.utils.safestring import SafeString, mark_safe

from crispy_forms.exceptions import CrispyError
from crispy_forms.utils import TEMPLATE_PACK
from portlets.models import Slot

import lfs.catalog.utils
import lfs.core.utils
import lfs.marketing.utils
from lfs.catalog.models import Category, Product, StaticBlock

register = Library()


@register.simple_tag(takes_context=True)
def addon_include(context: Context, app_label: str, template_name: str) -> SafeString:
    """Render ``template_name`` with the current context only when the add-on ``app_label`` is installed.

    The theme supports optional add-ons (bulk prices, samples, carousel, Google Tag Manager, ...). Their template tags
    can only be loaded when they are installed, so the parts that use them live in their own templates under
    ``lfs_theme/addons/``, which this tag renders only for installed add-ons.
    """
    if not apps.is_installed(app_label):
        return mark_safe("")
    return mark_safe(render_to_string(template_name, context.flatten(), request=context.get("request")))


@register.simple_tag
def addon_installed(app_label: str) -> bool:
    """Return whether the add-on ``app_label`` is installed, for markup that only an add-on's JavaScript uses."""
    return apps.is_installed(app_label)


@register.simple_tag
def currency_code() -> str:
    """Return the shop's currency as ISO 4217 code (setting ``LFS_CURRENCY``), for structured data."""
    return getattr(settings, "LFS_CURRENCY", "EUR")


@register.simple_tag(takes_context=True)
def site_name(context: Context) -> str:
    """Return the shop's name, appended to page titles and given as og:site_name."""
    return lfs.core.utils.get_default_shop(context.get("request")).name


@register.inclusion_tag("lfs_theme/categories_footer.html")
def categories_footer() -> dict[str, Any]:
    """Display the top-level categories and their children in the footer."""
    return {"categories": Category.objects.filter(parent=None, exclude_from_navigation=False)}


class FooterNode(Node):
    """Put the first three static blocks into the context as ``footer``, for the footer columns."""

    def render(self, context: Context) -> str:
        """Set ``footer`` in the context; renders nothing."""
        context["footer"] = StaticBlock.objects.all()[:3]
        return ""


@register.tag("footer")
def do_footer(parser: Parser, token: Token) -> FooterNode:
    """Put the first three static blocks into the context as ``footer``."""
    bits = token.split_contents()
    if len(bits) != 1:
        raise TemplateSyntaxError(f"{bits[0]} tag needs no arguments")
    return FooterNode()


class TopsellerNode(Node):
    """Put the top sellers into the context as ``topseller``, in rows of five.

    On a product or category page the top sellers of that category, otherwise those of the whole shop.
    """

    def render(self, context: Context) -> str:
        """Set ``topseller`` in the context; renders nothing."""
        obj = context.get("category") or context.get("product")
        if obj is None:
            topseller = lfs.marketing.utils.get_topseller()
        elif isinstance(obj, Product):
            category = lfs.catalog.utils.get_current_product_category(context.get("request"), obj)
            topseller = lfs.marketing.utils.get_topseller_for_category(category, 5)
        else:
            topseller = lfs.marketing.utils.get_topseller_for_category(obj, 5)
        context["topseller"] = lfs.core.utils.getLOL(topseller, 5)
        return ""


@register.tag("topseller")
def do_topseller(parser: Parser, token: Token) -> TopsellerNode:
    """Put the top sellers into the context as ``topseller``."""
    bits = token.split_contents()
    if len(bits) != 1:
        raise TemplateSyntaxError(f"{bits[0]} tag needs no arguments")
    return TopsellerNode()


@register.inclusion_tag("lfs_theme/top_nav.html", takes_context=True)
def top_nav(context: Context) -> dict[str, Any]:
    """Build the top navigation: top-level categories with up to two levels of children."""
    request = context.get("request")
    current_object = context.get("product") or context.get("category")
    active_top_category = lfs.catalog.utils.get_current_top_category(request, current_object)
    path = request.path if request else ""

    top_level_categories = []
    for root in Category.objects.filter(parent=None, exclude_from_navigation=False):
        children = []
        for child in root.get_children().filter(exclude_from_navigation=False):
            grandchildren = [
                {"title": c.name, "url": c.get_absolute_url(), "current": c.get_absolute_url() == path}
                for c in child.get_children()
                if not c.exclude_from_navigation
            ]
            children.append(
                {
                    "title": child.name,
                    "url": child.get_absolute_url(),
                    "image": child.get_image(),
                    "children": grandchildren,
                    "current": child.get_absolute_url() == path,
                }
            )
        top_level_categories.append(
            {
                "id": root.id,
                "url": root.get_absolute_url(),
                "name": root.name,
                "current": bool(active_top_category and active_top_category.id == root.id),
                "children": children,
            }
        )

    return {"categories": top_level_categories, "request": request, "current_object": current_object}


@register.filter(name="as_crispy_field_no_label")
def as_crispy_field_no_label(
    field: boundfield.BoundField, template_pack: str = TEMPLATE_PACK, label_class: str = "", field_class: str = ""
) -> SafeString:
    """Render a form field like crispy-forms' ``as_crispy_field``, but without its label."""
    if not isinstance(field, boundfield.BoundField) and settings.DEBUG:
        raise CrispyError("|as_crispy_field_no_label got passed an invalid or inexistent field")

    attributes = {
        "field": field,
        "form_show_errors": True,
        "form_show_labels": False,
        "label_class": label_class,
        "field_class": field_class,
    }
    helper = getattr(field.form, "helper", None)
    template_path = None
    if helper is not None:
        attributes.update(helper.get_attributes(template_pack))
        template_path = helper.field_template
    template = get_template(template_path or f"{template_pack}/field.html")
    return template.render(attributes)


class SlotsInformationNode(Node):
    """Put ``SlotLeft``, ``SlotRight`` (whether the slot has portlets) into the context.

    For the current category, product, or page; otherwise for the shop. Results are cached.
    """

    def render(self, context: Context) -> str:
        """Set one ``Slot<name>`` flag per slot in the context; renders nothing."""
        obj = context.get("category") or context.get("product") or context.get("page")
        if obj is None or obj.__class__.__name__.lower() not in ("category", "product", "page"):
            obj = lfs.core.utils.get_default_shop(context.get("request"))

        slots = cache.get("slots")
        if slots is None:
            slots = list(Slot.objects.all())
            cache.set("slots", slots)

        for slot in slots:
            cache_key = f"has-portlets-{obj.__class__.__name__}-{obj.id}-{slot.name}"
            has_portlets = cache.get(cache_key)
            if has_portlets is None:
                has_portlets = slot.has_portlets(obj)
                cache.set(cache_key, has_portlets)
            context[f"Slot{slot.name}"] = has_portlets
        return ""


@register.tag("slots_information")
def do_slots_information(parser: Parser, token: Token) -> SlotsInformationNode:
    """Put the ``Slot<name>`` flags of the current object into the context."""
    bits = token.split_contents()
    if len(bits) != 1:
        raise TemplateSyntaxError(f"{bits[0]} tag needs no arguments")
    return SlotsInformationNode()


@register.inclusion_tag("lfs/mail/mail_html_footer.html", takes_context=True)
def email_html_footer(context: Context) -> dict[str, Any]:
    """Render the HTML footer of the shop's e-mails."""
    return {"shop": lfs.core.utils.get_default_shop(context.get("request"))}


@register.inclusion_tag("lfs/mail/mail_text_footer.html", takes_context=True)
def email_text_footer(context: Context) -> dict[str, Any]:
    """Render the plain-text footer of the shop's e-mails."""
    return {"shop": lfs.core.utils.get_default_shop(context.get("request"))}


@register.filter
def cart_delivery_time(cart: Any, request: Any) -> Any:
    """Return the longest delivery time of the cart's products, for the checkout summary; None without a cart."""
    return cart.get_delivery_time(request) if cart else None
