from rest_framework.routers import DefaultRouter

from thorpat.api.v1.users.views import UserView

router = DefaultRouter()
router.register(r"users", UserView, basename="user")
