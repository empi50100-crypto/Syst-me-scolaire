from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Returns the value for a key in a dictionary.
    Usage: {{ mydict|get_item:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


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


@register.filter
def min_note(evals):
    """Retourne la note minimale d'une liste d'évaluations"""
    if not evals:
        return None
    try:
        notes = [e.note for e in evals if hasattr(e, 'note') and e.note is not None]
        return min(notes) if notes else None
    except:
        return None


@register.filter
def max_note(evals):
    """Retourne la note maximale d'une liste d'évaluations"""
    if not evals:
        return None
    try:
        notes = [e.note for e in evals if hasattr(e, 'note') and e.note is not None]
        return max(notes) if notes else None
    except:
        return None


@register.filter
def avg_note(evals):
    """Retourne la moyenne d'une liste d'évaluations"""
    if not evals:
        return None
    try:
        notes = [e.note for e in evals if hasattr(e, 'note') and e.note is not None]
        return sum(notes) / len(notes) if notes else None
    except:
        return None
