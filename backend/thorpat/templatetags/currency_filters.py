import decimal

from django import template
from django.conf import settings

register = template.Library()

# ตัวอย่างอัตราแลกเปลี่ยน (ในระบบจริงควรดึงมาจากฐานข้อมูลหรือ API)
EXCHANGE_RATES = {
    "THB": decimal.Decimal("1.0"),
    "USD": decimal.Decimal("0.027"),
    "EUR": decimal.Decimal("0.025"),
}

CURRENCY_SYMBOLS = {
    "THB": "฿",
    "USD": "$",
    "EUR": "€",
}


@register.simple_tag(takes_context=True)
def convert_currency(context, value):
    """
    Converts a value to the target currency.
    Assumes the base currency is always the default (THB).
    """
    target_currency = context.get("currency", settings.THORPAT_DEFAULT_CURRENCY)

    if value is None:
        value = decimal.Decimal("0.0")

    if not isinstance(value, decimal.Decimal):
        try:
            value = decimal.Decimal(str(value))
        except (decimal.InvalidOperation, TypeError):
            return ""

    # แปลงราคาจาก THB (สกุลเงินหลัก) เป็นสกุลเงินเป้าหมาย
    try:
        rate = EXCHANGE_RATES[target_currency]
        converted_value = value * rate
    except KeyError:
        # หากไม่พบอัตราแลกเปลี่ยน ให้แสดงค่าเดิม
        converted_value = value

    symbol = CURRENCY_SYMBOLS.get(target_currency, "")

    return f"{symbol}{converted_value:,.2f}"
