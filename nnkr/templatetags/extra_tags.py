from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import re

register = template.Library()

# To read cookies within django template, from http://stackoverflow.com/questions/26301447/django-read-cookie-in-template-tag
@register.simple_tag(takes_context = True)
def cookie(context, cookie_name): # could feed in additional argument to use as default value
    request = context['request']
    result = request.COOKIES.get(cookie_name,'') # I use blank as default value
    return result

@register.filter
def addstr(arg1, arg2):
    return str(arg1) + str(arg2)


@register.filter(needs_autoescape=True)
def initial_letter_filter(text, autoescape=True):
    first, other = text[0], text[1:]
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    result = '<b>%s</b>%s' % (esc(first), esc(other))
    return mark_safe(result)

@register.filter(needs_autoescape=True)
def anchor_filter(_text, autoescape=True):
    text = _text[:] # copy to avoid escape.
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    
    result = ""
    items = re.split('(>>[0-9]+)', text)
    for item in items:
        if re.search('>>[0-9]+', item):
            num = re.search('[0-9]+', item).group()
            result += '<a href="#comment-%s" class="onMouse" name="%s">%s</a>' % (num,num,esc(item))
        else:
            result += '%s' % esc(item)

    return mark_safe(result)