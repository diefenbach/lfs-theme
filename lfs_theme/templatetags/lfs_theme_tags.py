# django imports
from django.core.cache import cache
from django.template import Library, Node, TemplateSyntaxError
from django.utils.translation import ugettext as _

# portlets imports
import portlets.utils
from portlets.models import Slot

# lfs imports
import lfs.core.utils

register = Library()


class SlotsInformationNode(Node):
    """
    """
    def render(self, context):
        request = context.get("request")
        obj = context.get("category") or context.get("product") or context.get("page")
        if obj is None or obj.__class__.__name__.lower() not in ('category', 'product', 'page'):
            obj = lfs.core.utils.get_default_shop(request)

        slots = cache.get("slots")
        if slots is None:
            slots = Slot.objects.all()
            cache.set("slots", slots)

        for slot in slots:
            cache_key = "has-portlets-%s-%s-%s" % (obj.__class__.__name__, obj.id, slot.name)
            has_portlets = cache.get(cache_key)
            if has_portlets is None:
                has_portlets = portlets.utils.has_portlets(obj, slot)
                cache.set(cache_key, has_portlets)

            context["Slot%s" % slot.name] = has_portlets

        cache_key = "content-class-%s-%s" % (obj.__class__.__name__, obj.id)
        content_class = cache.get(cache_key)
        if content_class is None:
            content_class = "span-24 last"
            if context.get("SlotLeft", None) and context.get("SlotRight", None):
                content_class = "span-15 padding-both"
            elif context.get("SlotLeft", None):
                content_class = "span-19 padding-left last"
            elif context.get("SlotRight", None):
                content_class = "span-20 padding-right"

            cache.set(cache_key, content_class)

        context["content_class"] = content_class
        return ''

def do_slots_information(parser, token):
    """Calculates some context variables based on displayed slots.
    """
    bits = token.contents.split()
    len_bits = len(bits)
    if len_bits != 1:
        raise TemplateSyntaxError(_('%s tag needs no argument') % bits[0])

    return SlotsInformationNode()

register.tag('slots_information', do_slots_information)


@register.inclusion_tag('lfs/mail/mail_html_footer.html', takes_context=True)
def email_html_footer(context):
    request = context.get('request', None)
    shop = lfs.core.utils.get_default_shop(request)
    return {
        "shop": shop
    }


@register.inclusion_tag('lfs/mail/mail_text_footer.html', takes_context=True)
def email_text_footer(context):
    request = context.get('request', None)
    shop = lfs.core.utils.get_default_shop(request)
    return {
        "shop": shop
    }
