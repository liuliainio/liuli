from django.utils.translation import ugettext as _

from estorecore.models.app import CustomManager
from estoreoperation.utils import string_with_title
from estoreoperation.app.models import Application


class AppUpdateNoScreenshots(Application):

    objects = CustomManager({'versions_count__gt': 1, 'has_icon__exact': False})

    class Meta:
        proxy = True
        app_label = string_with_title("updateapps", _("App Updates"))
        verbose_name = _("Update without Screenshots")
        verbose_name_plural = _("Update without Screenshots")


class AppUpdateWithScreenshots(Application):

    objects = CustomManager({'versions_count__gt': 1, 'has_icon__exact': True})

    class Meta:
        proxy = True
        app_label = string_with_title("updateapps", _("App Updates"))
        verbose_name = _("Update with Screenshots")
        verbose_name_plural = _("Update with Screenshots")
