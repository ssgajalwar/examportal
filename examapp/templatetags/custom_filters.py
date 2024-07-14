from django import template

register = template.Library()

@register.filter(name='removespaces')
def removespaces(value):
    return value.replace(' ', '')