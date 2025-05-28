from ninja import Router

from .endpoints import auth, users, error, profiles

v1 = Router()
v1.add_router("/auth", auth.router)
v1.add_router("/users", users.router)
v1.add_router("/error", error.router)
v1.add_router("/profiles", profiles.router)
