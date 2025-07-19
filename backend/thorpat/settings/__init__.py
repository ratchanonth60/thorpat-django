from .dev import *  # noqa: F401, F403


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {  # Formatter สำหรับ console ทั่วไป (ถ้าไม่ใช้ colorlog)
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "colored_console": {  # Formatter ใหม่สำหรับ console ที่มีสีสัน
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(asctime)s%(reset)s %(name)s: %(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            "secondary_log_colors": {},
            "style": "%",  # colorlog ใช้ %-style formatting
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",  # ใน development อาจจะต้องการ DEBUG
            "class": "logging.StreamHandler",
            # 'formatter': 'simple', # เปลี่ยนไปใช้ colored_console
            "formatter": "colored_console"
            if DEBUG
            else "simple",  # ใช้ colored_console ถ้า DEBUG=True
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs/django_app.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        # (ทางเลือก) Sentry Handler (ถ้าไม่ใช้ LoggingIntegration ของ Sentry SDK โดยตรง)
        # โดยทั่วไป LoggingIntegration จะทำงานได้ดี แต่ถ้าต้องการ control ละเอียดขึ้นก็สามารถเพิ่ม handler ได้
        # 'sentry': {
        #     'level': 'ERROR', # ส่งเฉพาะ error ขึ้นไป
        #     'class': 'sentry_sdk.integrations.logging.EventHandler',
        #     'formatter': 'verbose', # Sentry จะใช้ข้อมูลจาก log record
        # },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],  # ถ้าใช้ Sentry Handler ก็เพิ่ม 'sentry' ที่นี่
            "level": "INFO",
            "propagate": True,
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "thorpat": {  # Logger สำหรับแอปพลิเคชันของคุณ
            "handlers": ["console", "file"],  # ถ้าใช้ Sentry Handler ก็เพิ่ม 'sentry'
            "level": "DEBUG",  # ใน development, production อาจจะเป็น INFO
            "propagate": False,
        },
        # ตัวอย่าง logger สำหรับ Django Ninja โดยเฉพาะ
        "ninja": {
            "handlers": ["console", "file"],
            "level": "INFO",  # หรือ DEBUG ถ้าต้องการดู log ของ Ninja มากขึ้น
            "propagate": False,
        },
        # ถ้าต้องการ log SQL queries (สำหรับ debug performance)
        # 'django.db.backends': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG', # จะแสดง SQL queries ทั้งหมด, ใช้เฉพาะตอน debug
        #     'propagate': False,
        # },
    },
}

# กำหนด Log Level ตาม DEBUG setting (ทางเลือก)
if DEBUG:
    LOGGING["handlers"]["console"]["level"] = "DEBUG"
    LOGGING["loggers"]["thorpat"]["level"] = "DEBUG"
    LOGGING["loggers"]["ninja"]["level"] = "DEBUG"
else:  # Production settings
    LOGGING["handlers"]["console"]["level"] = "INFO"
    LOGGING["handlers"]["console"]["formatter"] = (
        "simple"  # ใน production console อาจจะไม่ต้องการสี
    )
    LOGGING["loggers"]["thorpat"]["level"] = "INFO"
    LOGGING["loggers"]["ninja"]["level"] = "INFO"
    # ใน production, file handler และ Sentry จะสำคัญกว่า
