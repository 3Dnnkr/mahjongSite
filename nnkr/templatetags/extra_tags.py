from django import template

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