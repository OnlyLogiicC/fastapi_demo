from typing import Literal

scopes = Literal["users:view", "users:edit", "items:view", "items:edit", "system_config"]

scopes_description: dict[scopes, str] = {
    "users:view": "Read a user's data",
    "users:edit": "Edit user's data",
    "items:view": "Read Items",
    "items:edit": "Edit Items",
    "system_config": "Edit system config",
}
