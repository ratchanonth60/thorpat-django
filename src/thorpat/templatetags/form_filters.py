from django import template
from django.forms import BoundField  # นำเข้า BoundField

register = template.Library()


# ฟังก์ชันช่วยสำหรับเพิ่ม/แก้ไข attribute ใน widget.attrs
def _set_widget_attr(field, attribute, value):
    """
    Sets or adds an attribute to the widget of a form field.
    Handles 'class' attribute by appending, others by setting.
    """
    # ตรวจสอบให้แน่ใจว่าเป็น BoundField และมี widget
    if not isinstance(field, BoundField) or not hasattr(field.field, "widget"):
        return field  # คืนค่า field เดิมหากไม่สามารถแก้ไข widget ได้ (เช่นไม่ใช่ form field)

    # สร้าง mutable copy ของ attrs เพื่อป้องกันการแก้ไข shared dictionary
    attrs = field.field.widget.attrs.copy()

    if attribute == "class":
        # สำหรับ class attribute, ให้เพิ่ม class ใหม่เข้าไป
        current_classes = attrs.get("class", "").split()
        new_classes = value.split()
        for cls in new_classes:
            if cls not in current_classes:
                current_classes.append(cls)
        attrs["class"] = " ".join(current_classes)
    else:
        # สำหรับ attribute อื่นๆ, ให้ตั้งค่าโดยตรง
        attrs[attribute] = value

    # สร้าง widget ใหม่ที่มี attrs ที่แก้ไขแล้ว
    # นี่เป็นวิธีที่ปลอดภัยกว่าการแก้ไข widget.attrs โดยตรง
    # เนื่องจากบาง widget อาจไม่รองรับการแก้ไข attrs หลังจากสร้างแล้ว
    field.field.widget.attrs = attrs

    return field  # สำคัญ: คืนค่า field object กลับไป ไม่ใช่ HTML ที่ render แล้ว


@register.filter(name="add_class")
def add_class(field, css_class):
    """
    Adds a CSS class to a form field's widget.
    Usage: {{ field|add_class:"your-class-name" }}
    """
    return _set_widget_attr(field, "class", css_class)


@register.filter(name="add_placeholder")
def add_placeholder(field, placeholder_text):
    """
    Adds a placeholder attribute to a form field's widget.
    Usage: {{ field|add_placeholder:"Enter your value here" }}
    """
    return _set_widget_attr(field, "placeholder", placeholder_text)


@register.filter(name="add_attr")
def add_attr(field, attributes_str):
    """
    Adds HTML attributes to a form field widget.

    Usage:
    {{ my_field|add_attr:"class: my-class, rows: 4, placeholder: Enter text" }}
    """
    # Start with the widget's existing attributes
    attrs = field.field.widget.attrs.copy()

    # Split the attribute string by comma to handle multiple attributes
    attributes = [attr.strip() for attr in attributes_str.split(",")]

    for attribute in attributes:
        # Split each attribute into key and value
        try:
            key, value = attribute.split(":", 1)
            key = key.strip()
            value = value.strip()

            # For the 'class' attribute, append to existing classes
            if key.lower() == "class":
                attrs[key] = f"{attrs.get(key, '')} {value}".strip()
            else:
                attrs[key] = value
        except ValueError:
            # Ignore incorrectly formatted attributes
            pass

    return field.as_widget(attrs=attrs)
