import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="jsondata")
def jsondata(value):
    return mark_safe(json.dumps(value).replace("'", "&#39;"))
