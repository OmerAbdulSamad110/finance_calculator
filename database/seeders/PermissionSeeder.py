from app.Models.Permission import Permission
from app.Http.Responses.JsonResponse import JsonResponse
from sqlalchemy.ext.asyncio import AsyncSession

grouped_permissions = {
    "Country": [
        {"label": "View Country", "slug": "view_country"},
        {"label": "Store Country", "slug": "store_country"},
        {"label": "Update Country", "slug": "update_country"},
        {"label": "Delete Country", "slug": "delete_country"},
    ],
    "City": [
        {"label": "View City", "slug": "view_city"},
        {"label": "Store City", "slug": "store_city"},
        {"label": "Update City", "slug": "update_city"},
        {"label": "Delete City", "slug": "delete_city"},
    ],
    "company": [
        {"label": "View Company", "slug": "view_company"},
        {"label": "Store Company", "slug": "store_company"},
        {"label": "Update Company", "slug": "update_company"},
        {"label": "Delete Company", "slug": "delete_company"},
    ],
    "user": [
        {"label": "View User", "slug": "view_user"},
        {"label": "Store User", "slug": "store_user"},
        {"label": "Update User", "slug": "update_user"},
        {"label": "Delete User", "slug": "delete_user"},
    ],
    "role": [
        {"label": "View Role", "slug": "view_role"},
        {"label": "Store Role", "slug": "store_role"},
        {"label": "Update Role", "slug": "update_role"},
        {"label": "Delete Role", "slug": "delete_role"},
    ],
    "permission": [
        {"label": "View Permission", "slug": "view_permission"},
        {"label": "Store Permission", "slug": "store_permission"},
        {"label": "Update Permission", "slug": "update_permission"},
        {"label": "Delete Permission", "slug": "delete_permission"},
    ],
    "setting": [
        {"label": "View Setting", "slug": "view_setting"},
        {"label": "Store Setting", "slug": "store_setting"},
        {"label": "Update Setting", "slug": "update_setting"},
        {"label": "Delete Setting", "slug": "delete_setting"},
    ],
    "mail": [
        {"label": "View Mail", "slug": "view_mail"},
        {"label": "Send Mail", "slug": "send_mail"},
    ],
    "mail_template": [
        {"label": "View Mail Template", "slug": "view_mail_template"},
        {"label": "Store Mail Template", "slug": "store_mail_template"},
        {"label": "Update Mail Template", "slug": "update_mail_template"},
        {"label": "Delete Mail Template", "slug": "delete_mail_template"},
    ],
}


async def seedPermissions(db: AsyncSession):
    for permissions in grouped_permissions.values():
        # store parent permission
        parent = Permission(**permissions[0])
        db.add(parent)
        await db.flush()

        for permission in permissions[1:]:
            child = Permission(**permission, parent_id=parent.id)
            db.add(child)
        await db.commit()
    return JsonResponse(message="Permissions seeded successfully.")
