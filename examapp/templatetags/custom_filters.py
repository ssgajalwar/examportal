from django import template

register = template.Library()

@register.filter(name='removespaces')
def removespaces(value):
    return value.replace(' ', '')

@register.filter(name='removeslash')
def removeslash(value):
    return value.replace('/','-')