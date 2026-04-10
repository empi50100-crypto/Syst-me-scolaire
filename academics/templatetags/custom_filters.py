from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None

@register.filter
def min_note(evaluations):
    if not evaluations:
        return 0
    notes = [float(e.note) for e in evaluations if hasattr(e, 'note')]
    return min(notes) if notes else 0

@register.filter
def max_note(evaluations):
    if not evaluations:
        return 0
    notes = [float(e.note) for e in evaluations if hasattr(e, 'note')]
    return max(notes) if notes else 0

@register.filter
def avg_note(evaluations):
    if not evaluations:
        return 0
    notes = [float(e.note) for e in evaluations if hasattr(e, 'note')]
    return sum(notes) / len(notes) if notes else 0

@register.filter
def avg_moyenne_generale(eleves_data):
    if not eleves_data:
        return 0
    notes = [e['moyenne_generale'] for e in eleves_data if e.get('moyenne_generale') is not None]
    return sum(notes) / len(notes) if notes else 0

@register.filter
def get_moyenne(matiere_data, key):
    if matiere_data is None:
        return None
    return matiere_data.get(key) if hasattr(matiere_data, 'get') else None
