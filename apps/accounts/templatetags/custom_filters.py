from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter to get dict value by key."""
    return dictionary.get(key)
