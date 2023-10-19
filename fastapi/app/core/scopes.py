from typing import Literal

scopes = Literal["users:view", "users:edit", "address:view", "address:edit", "system_config"]

scopes_description: dict[scopes, str] = {
    "users:view": "Read a user's data",
    "users:edit": "Edit user's data",
    "address:view": "Read addresses",
    "address:edit": "Edit addresses",
    "system_config": "Edit system config",
}
