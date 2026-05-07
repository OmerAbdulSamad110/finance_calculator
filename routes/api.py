from app.Http.Controllers.AuthController import AuthController
from app.Http.Controllers.CompanyController import CompanyController
from app.Http.Controllers.UserController import UserController
from app.Http.Controllers.RoleController import RoleController
from app.Http.Controllers.PermissionController import PermissionController
from fastapi import APIRouter, Depends
from app.Http.Responses.ValidationResponse import ValidationResponse

from app.Http.Middlewares.AuthMiddleware import handle as auth
from app.Http.Middlewares.PermMiddleware import can
from app.Http.Middlewares.HasRoleMiddleware import has

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
company_controller = CompanyController()
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
    # Country routes as a user with authorization
    (
        "/v1/countries",
        company_controller.index,
        ["GET"],
        # can(permissions=["view_country"]),
    ),
    (
        "/v1/countries/{id}",
        company_controller.show,
        ["GET"],
        # can(permissions=["view_country"]),
    ),
    (
        "/v1/countries",
        company_controller.store,
        ["POST"],
        # can(permissions=["store_country"]),
    ),
    (
        "/v1/countries/{id}",
        company_controller.update,
        ["PUT"],
        # can(permissions=["update_country"]),
    ),
    (
        "/v1/countries/{id}",
        company_controller.delete,
        ["DELETE"],
        # can(permissions=["delete_country"]),
    ),
    ("/v1/countries/list", company_controller.list, ["GET"]),
    # City routes as a user with authorization
    (
        "/v1/cities",
        company_controller.index,
        ["GET"],
        # can(permissions=["view_city"]),
    ),
    (
        "/v1/cities/{id}",
        company_controller.show,
        ["GET"],
        # can(permissions=["view_city"]),
    ),
    (
        "/v1/cities",
        company_controller.store,
        ["POST"],
        # can(permissions=["store_city"]),
    ),
    (
        "/v1/cities/{id}",
        company_controller.update,
        ["PUT"],
        # can(permissions=["update_city"]),
    ),
    (
        "/v1/cities/{id}",
        company_controller.delete,
        ["DELETE"],
        # can(permissions=["delete_city"]),
    ),
    ("/v1/cities/list", company_controller.list, ["GET"]),
    # Company routes as a user with authorization
    (
        "/v1/companies",
        company_controller.index,
        ["GET"],
        # can(permissions=["view_company"]),
    ),
    (
        "/v1/companies/{id}",
        company_controller.show,
        ["GET"],
        # can(permissions=["view_company"]),
    ),
    (
        "/v1/companies",
        company_controller.store,
        ["POST"],
        # can(permissions=["store_company"]),
    ),
    (
        "/v1/companies/{id}",
        company_controller.update,
        ["PUT"],
        # can(permissions=["update_company"]),
    ),
    (
        "/v1/companies/{id}",
        company_controller.delete,
        ["DELETE"],
        # can(permissions=["delete_company"]),
    ),
    ("/v1/companies/list", company_controller.list, ["GET"]),
    # User routes as a user with authorization
    (
        "/v1/users/list",
        user_controller.list,
        ["GET"],
        #  can(permissions=["view_user"])
    ),
    ("/v1/users", user_controller.index, ["GET"], can(permissions=["view_user"])),
    ("/v1/users/{id}", user_controller.show, ["GET"], can(permissions=["view_user"])),
    ("/v1/users", user_controller.store, ["POST"], can(permissions=["store_user"])),
    (
        "/v1/users/{id}/info",
        user_controller.updateInfo,
        ["PUT"],
        can(permissions=["update_user"]),
    ),
    (
        "/v1/users/{id}/password",
        user_controller.updatePassword,
        ["PUT"],
        can(permissions=["update_user"]),
    ),
    (
        "/v1/users/{id}",
        user_controller.delete,
        ["DELETE"],
        can(permissions=["delete_user"]),
    ),
    # Role routes as a user with authorization
    (
        "/v1/roles/list",
        role_controller.list,
        ["GET"],
        #  can(permissions=["view_role"])
    ),
    (
        "/v1/roles",
        role_controller.index,
        ["GET"],
        #  can(permissions=["view_role"])
    ),
    (
        "/v1/roles/{id}",
        role_controller.show,
        ["GET"],
        #  can(permissions=["view_role"])
    ),
    (
        "/v1/roles",
        role_controller.store,
        ["POST"],
        #  can(permissions=["store_role"])
    ),
    (
        "/v1/roles/{id}",
        role_controller.update,
        ["PUT"],
        # can(permissions=["update_role"]),
    ),
    (
        "/v1/roles/{id}",
        role_controller.delete,
        ["DELETE"],
        # can(permissions=["delete_role"]),
    ),
    # Permission routes as a user with authorization
    (
        "/v1/permissions/list",
        permission_controller.list,
        ["GET"],
        # can(permissions=["view_permission"]),
    ),
    (
        "/v1/permissions",
        permission_controller.index,
        ["GET"],
        # can(permissions=["view_permission"]),
    ),
    (
        "/v1/permissions/{id}",
        permission_controller.show,
        ["GET"],
        # can(permissions=["view_permission"]),
    ),
    (
        "/v1/permissions",
        permission_controller.store,
        ["POST"],
        # can(permissions=["store_permission"]),
    ),
    (
        "/v1/permissions/{id}",
        permission_controller.update,
        ["PUT"],
        # can(permissions=["update_permission"]),
    ),
    (
        "/v1/permissions/{id}",
        permission_controller.delete,
        ["DELETE"],
        # can(permissions=["delete_permission"]),
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
