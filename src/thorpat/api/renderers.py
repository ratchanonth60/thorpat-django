from rest_framework.renderers import JSONRenderer


class CustomAPIRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_obj = renderer_context[  # type: ignore[assignment]
            "response"
        ]  # ควรใช้ response_obj แทน response เพื่อไม่ให้สับสน
        http_status = response_obj.status_code

        # ตรวจสอบว่า data ที่เข้ามา (ซึ่งคือ response_obj.data)
        # ถูกจัดรูปแบบตาม ResponseAPI แล้วหรือยัง
        # โดยดูจาก key ที่คาดหวังเช่น 'success', 'message', 'data', 'errors'
        if (
            isinstance(data, dict)
            and "success" in data
            and "message" in data
            and "data" in data
            and "errors" in data
        ):
            # ถ้า data ถูกจัดรูปแบบมาแล้ว (เช่น มาจาก custom_exception_handler ที่ใช้ ResponseAPI)
            # ให้ render data นั้นไปเลย โดยไม่ต้องจัดรูปแบบซ้ำ
            # และที่สำคัญคือ http_status ที่ใช้ใน response_data ของ ResponseAPI
            # ควรจะตรงกับ http_status ของ response object จริงๆ
            # ซึ่ง ResponseAPI class ของคุณจัดการเรื่องนี้แล้วตอนสร้าง response_data
            # และส่ง status ที่ถูกต้องให้ super().__init__
            return super().render(data, accepted_media_type, renderer_context)

        # ถ้า data ยังไม่ได้ถูกจัดรูปแบบ (เช่น มาจาก view ที่ return dict/list ธรรมดา
        # หรือมาจาก DRF exception handler ดั้งเดิม ถ้า custom_exception_handler ไม่ได้ใช้ ResponseAPI)
        errors_payload = None
        data_payload = None
        message_for_renderer = None  # เปลี่ยนชื่อ message variable

        if http_status >= 400:
            # data ที่เข้ามาตรงนี้คือ error details ดั้งเดิมจาก DRF (เช่น {'detail': 'Not found'})
            errors_payload = data
            data_payload = None  # ไม่มี data payload สำหรับ error

            # พยายามดึง message จาก error details
            if isinstance(data, dict) and "detail" in data and len(data.keys()) == 1:
                message_for_renderer = data.get("detail", "Request failed.")
            elif (
                isinstance(data, list)
                and data
                and isinstance(data[0], dict)
                and "detail" in data[0]
            ):
                message_for_renderer = data[0].get("detail", "Request failed.")
            elif isinstance(data, dict):  # Validation Error ทั่วไป
                message_for_renderer = "Validation failed."
            else:
                message_for_renderer = str(data) if data else "Request failed."
                if data and not isinstance(
                    data, dict
                ):  # ถ้า data เป็น string หรือ list ธรรมดา
                    errors_payload = {"non_field_errors": [str(data)]}

        else:  # กรณี Success (http_status < 300)
            data_payload = data
            errors_payload = None
            message_for_renderer = "Success"

        # สร้างโครงสร้าง response_data ตามรูปแบบ ResponseAPI
        response_data_formatted_by_renderer = {
            "code": http_status,
            "success": http_status < 300,
            "message": message_for_renderer,
            "data": data_payload,
            "errors": errors_payload,
        }
        return super().render(
            response_data_formatted_by_renderer, accepted_media_type, renderer_context
        )
