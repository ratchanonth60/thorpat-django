from django import template
from django.forms import BoundField

register = template.Library()

def _set_widget_attr(field, attribute, value):
    """
    Helper function to safely set or add an attribute to a form field's widget.
    It returns the field object to allow for filter chaining.
    """
    # Make sure we have a field that we can modify
    if not isinstance(field, BoundField) or not hasattr(field.field, "widget"):
        return field

    # Make a mutable copy of the widget's attributes
    attrs = field.field.widget.attrs.copy()

    # Special handling for the 'class' attribute to append new classes
    if attribute.lower() == "class":
        current_classes = attrs.get("class", "").split()
        new_classes = value.split()
        for cls in new_classes:
            if cls not in current_classes:
                current_classes.append(cls)
        attrs["class"] = " ".join(current_classes)
    else:
        # For other attributes, just set or overwrite the value
        attrs[attribute] = value

    # Update the widget's attributes dictionary
    field.field.widget.attrs = attrs
    
    # IMPORTANT: Return the field object itself to allow for chaining
    return field


@register.filter(name="add_class")
def add_class(field, css_class):
    """
    Adds a CSS class to a form field's widget.
    Usage: {{ field|add_class:"your-class" }}
    """
    return _set_widget_attr(field, "class", css_class)


@register.filter(name="add_placeholder")
def add_placeholder(field, placeholder_text):
    """
    Adds a placeholder attribute to a form field's widget.
    Usage: {{ field|add_placeholder:"Your placeholder" }}
    """
    return _set_widget_attr(field, "placeholder", placeholder_text)


@register.filter(name="add_attr")
def add_attr(field, attr_str):
    """
    Adds a single HTML attribute to a form field's widget. Allows chaining.
    The attribute must be in "key:value" format.
    Usage: {{ my_field|add_attr:"rows:4"|add_attr:"hx-post:/url/" }}
    """
    try:
        # Split the input string into an attribute name and value
        attr, value = attr_str.split(":", 1)
        return _set_widget_attr(field, attr.strip(), value.strip())
    except ValueError:
        # If the format is wrong (e.g., no colon), just return the field unchanged
        return field

