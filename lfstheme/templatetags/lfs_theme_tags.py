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
        
        for slot in Slot.objects.all():
            context["Slot%s" % slot.name] = portlets.utils.has_portlets(slot, object)

        content_class = "span-24 last"
        if context.get("SlotLeft", None) and context.get("SlotRight", None):
            content_class = "span-15 padding-both"
        elif context.get("SlotLeft", None):
            content_class = "span-19 padding-left last"
        elif context.get("SlotRight", None):
            content_class = "span-20 padding-right"
        
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