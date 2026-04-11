from django import template

register = template.Library()

@register.filter
def initial(value):
    if value:
        return value[0].upper()
    return ''


@register.filter
def filter_niveau(configs, niveau):
    for config in configs:
        if config.niveau == niveau:
            return config
    return None
