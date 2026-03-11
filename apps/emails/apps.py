from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class EmailsConfig(AppConfig):
    name = "apps.emails"
    verbose_name = _("Emails")
