from app.Models.Permission import Permission
from app.Http.Responses.JsonResponse import JsonResponse
from sqlalchemy.ext.asyncio import AsyncSession

grouped_permissions = {
    "user": [
        {"label": "View User", "slug": "view_user"},
        {"label": "Create User", "slug": "create_user"},
        {"label": "Update User", "slug": "update_user"},
        {"label": "Delete User", "slug": "delete_user"},
    ],
    "role": [
        {"label": "View Role", "slug": "view_role"},
        {"label": "Create Role", "slug": "create_role"},
        {"label": "Update Role", "slug": "update_role"},
        {"label": "Delete Role", "slug": "delete_role"},
    ],
    "permission": [
        {"label": "View Permission", "slug": "view_permission"},
        {"label": "Create Permission", "slug": "create_permission"},
        {"label": "Update Permission", "slug": "update_permission"},
        {"label": "Delete Permission", "slug": "delete_permission"},
    ],
    "permission_role": [
        {"label": "View Permission Role", "slug": "view_permission_role"},
        {"label": "Assign Permission Role", "slug": "sync_permission_role"},
    ],
    "setting": [
        {"label": "View Setting", "slug": "view_setting"},
        {"label": "Create Setting", "slug": "create_setting"},
        {"label": "Update Setting", "slug": "update_setting"},
        {"label": "Delete Setting", "slug": "delete_setting"},
    ],
    "mail": [
        {"label": "View Mail", "slug": "view_mail"},
        {"label": "Send Mail", "slug": "send_mail"},
    ],
    "mail_template": [
        {"label": "View Mail Template", "slug": "view_mail_template"},
        {"label": "Create Mail Template", "slug": "create_mail_template"},
        {"label": "Update Mail Template", "slug": "update_mail_template"},
        {"label": "Delete Mail Template", "slug": "delete_mail_template"},
    ],
}


async def seedPermissions(db: AsyncSession):
    for permissions in grouped_permissions.values():
        # create parent permission
        parent = Permission(**permissions[0])
        db.add(parent)
        await db.flush()

        for permission in permissions[1:]:
            child = Permission(**permission, parent_id=parent.id)
            db.add(child)
        await db.commit()
    return JsonResponse(message="Permissions seeded successfully.")
