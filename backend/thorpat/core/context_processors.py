from django.conf import settings


def currency(request):
    """
    A context processor to add the current currency to the context.
    """
    # ดึงสกุลเงินที่ผู้ใช้เลือกจาก session, ถ้าไม่มีให้ใช้ค่า default
    selected_currency = request.session.get(
        "currency", settings.THORPAT_DEFAULT_CURRENCY
    )

    return {
        "currency": selected_currency,
        "available_currencies": settings.THORPAT_AVAILABLE_CURRENCIES,
    }
