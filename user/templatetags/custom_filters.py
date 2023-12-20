from django import template
import hashlib

register = template.Library()

@register.filter
def img_from_name(name):
    hash = hashlib.md5(name.lower().encode('utf-8')).hexdigest()
    num = "1"
    for i in list(hash):
        if i.isdigit() and 1 <= int(i) < 7:
            num = i
            break
    return f"https://bootdey.com/img/Content/avatar/avatar{num}.png"
