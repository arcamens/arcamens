from django import template
from django.core.paginator import Paginator
from os.path import basename
from django.utils import timezone

register = template.Library()

@register.filter
def bname(filename):
    return basename(filename)








