from django import template
from django.core.paginator import Paginator

register = template.Library()

@register.filter
def partition(objects, n_items):
    paginator = Paginator(objects, n_items)
    for indi in paginator.page_range:
        yield paginator.page(indi)
    


