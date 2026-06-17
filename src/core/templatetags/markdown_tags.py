from django import template
from django.utils.safestring import mark_safe

from ..utils.markdown import render_markdown

register = template.Library()


@register.filter(name='markdown')
def markdown_filter(text):
    return mark_safe(render_markdown(text))
