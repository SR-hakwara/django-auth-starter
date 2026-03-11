import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

templates_dir = BASE_DIR / "templates"

replacements = {
    "users:login": "authentication:login",
    "users:register": "authentication:register",
    "users:logout": "authentication:logout",
    "users:activation_sent": "authentication:activation_sent",
    "users:activate": "authentication:activate",
    "users:resend_activation": "profiles:resend_activation",
    "users:password_reset": "authentication:password_reset",
    "users:password_reset_done": "authentication:password_reset_done",
    "users:password_reset_confirm": "authentication:password_reset_confirm",
    "users:profile": "profiles:profile",
    "users:profile_update": "profiles:profile_update",
    "users:password_change": "profiles:password_change",
}

for root, _, files in os.walk(templates_dir):
    for file in files:
        if file.endswith(".html"):
            path = Path(root) / file
            content = path.read_text("utf-8")
            new_content = content
            for old, new in replacements.items():
                new_content = new_content.replace(old, new)
            if new_content != content:
                path.write_text(new_content, "utf-8")
                print(f"Updated {path}")
