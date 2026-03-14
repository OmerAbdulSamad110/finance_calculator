from app.Http.Controllers.AuthController import AuthController
from app.Http.Controllers.UserController import UserController
from app.Http.Controllers.RoleController import RoleController
from app.Http.Controllers.PermissionController import PermissionController
from fastapi import APIRouter, Depends
from app.Http.Responses.ValidationResponse import ValidationResponse
from app.Http.Middlewares.AuthMiddleware import handle as auth
from app.Http.Middlewares.PermMiddleware import can

api_router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={
        404: {"description": "Not found"},
        400: {"model": ValidationResponse},
        422: {"model": None},
    },
)
# Controllers
auth_controller = AuthController()
user_controller = UserController()
role_controller = RoleController()
permission_controller = PermissionController()

routes = [
    # Auth routes as a guest
    ("/v1/auth/login", auth_controller.login, ["POST"]),
    ("/v1/auth/register", auth_controller.register, ["POST"]),
    ("/v1/auth/forgot-password", auth_controller.forgotPassword, ["POST"]),
    ("/v1/auth/reset-password", auth_controller.resetPassword, ["POST"]),
    ("/v1/auth/verify", auth_controller.verify, ["GET"]),
    # Auth routes as a user
    ("/v1/auth/refresh-token", auth_controller.refreshToken, ["POST"]),
    ("/v1/auth/logout", auth_controller.logout, ["POST"], auth),
    ("/v1/auth/me", auth_controller.me, ["GET"], auth),
    # User routes as a user with authorization
    ("v1/users/list", user_controller.list, ["GET"]),
    (
        "v1/users",
        user_controller.index,
        ["GET"],
        can(permissions=["view_user"]),
    ),
    ("v1/users/{id}", user_controller.show, ["GET"], can(permissions=["view_user"])),
    ("v1/users", user_controller.store, ["POST"], can(permissions=["create_user"])),
    (
        "v1/users/{id}",
        user_controller.update,
        ["PUT"],
        can(permissions=["update_user"]),
    ),
    (
        "v1/users/{id}",
        user_controller.delete,
        ["DELETE"],
        can(permissions=["delete_user"]),
    ),
    # Role routes as a user with authorization
    ("v1/roles/list", role_controller.list, ["GET"]),
    ("v1/roles", role_controller.index, ["GET"], can(permissions=["view_role"])),
    ("v1/roles/{id}", role_controller.show, ["GET"], can(permissions=["view_role"])),
    ("v1/roles", role_controller.store, ["POST"], can(permissions=["create_role"])),
    (
        "v1/roles/{id}",
        role_controller.update,
        ["PUT"],
        can(permissions=["update_role"]),
    ),
    (
        "v1/roles/{id}",
        role_controller.delete,
        ["DELETE"],
        can(permissions=["delete_role"]),
    ),
    (
        "v1/roles/{role_id}/sync-permissions",
        role_controller.syncRolePermissions,
        ["POST"],
        can(permissions=["sync_permission_role"]),
    ),
    # Permission routes as a user with authorization
    (
        "v1/permissions",
        permission_controller.index,
        ["GET"],
        can(permissions=["view_permission"]),
    ),
    (
        "v1/permissions/{id}",
        permission_controller.show,
        ["GET"],
        can(permissions=["view_permission"]),
    ),
    (
        "v1/permissions",
        permission_controller.store,
        ["POST"],
        can(permissions=["create_permission"]),
    ),
    (
        "v1/permissions/{id}",
        permission_controller.update,
        ["PUT"],
        can(permissions=["update_permission"]),
    ),
    (
        "v1/permissions/{id}",
        permission_controller.delete,
        ["DELETE"],
        can(permissions=["delete_permission"]),
    ),
]


def registerRoutes():
    for path, handler, methods, *rest in routes:
        middleware = rest[0] if rest else None
        if middleware is not None:
            middleware = (
                [Depends(middleware)]
                if middleware is not list
                else [Depends(middleware) for middleware in middleware]
            )
        api_router.add_api_route(
            path, handler, methods=methods, dependencies=middleware
        )
    return api_router
