from django import template
from django.forms.boundfield import BoundField

register = template.Library()


@register.filter(name="add_class")
def add_class(bound_field, css_class_str):
    if not isinstance(bound_field, BoundField):
        return bound_field

    try:
        existing_classes = bound_field.field.widget.attrs.get("class", "")
    except AttributeError:
        existing_classes = ""

    new_classes = " ".join(filter(None, [existing_classes, css_class_str]))
    return bound_field.as_widget(attrs={"class": new_classes})
