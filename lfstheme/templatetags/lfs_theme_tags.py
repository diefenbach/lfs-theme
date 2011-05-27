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

        object = context.get("category") or context.get("product")

        if object is None:
            object = lfs.core.utils.get_default_shop()

        slots = cache.get("slots")
        if slots is None:
            slots = Slot.objects.all()
            cache.set("slots", slots)

        for slot in slots:
            cache_key = "has-portlets-%s-%s-%s" % (object.__class__.__name__, object.id, slot.name)
            has_portlets = cache.get(cache_key)
            if has_portlets is None:
                has_portlets = portlets.utils.has_portlets(object, slot)
                cache.set(cache_key, has_portlets)

            context["Slot%s" % slot.name] = has_portlets

        cache_key = "content-class-%s-%s" % (object.__class__.__name__, object.id)
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