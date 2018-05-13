from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.simple_tag(name='avatar')
def avatar(file):
    return file.url if file else settings.STATIC_URL + 'user.png'

