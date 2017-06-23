from django.utils.translation import ugettext as _

from estorecore.models.app import CustomManager
from estorecore.models.constants import REVIEW_STATUS
from estoreoperation.utils import string_with_title
from estoreoperation.app.models import Application, AppVersion, SubjectItem


class SearchApp(Application):
    objects = CustomManager({'review_status__exact': REVIEW_STATUS.APPROVED})

    class Meta:
        proxy = True
        app_label = string_with_title("utilities", _("Utilities"))
        verbose_name = _("Application")
        verbose_name_plural = _("Applications")


class AppVersionList(AppVersion):
    class Meta:
        proxy = True
        app_label = string_with_title("utilities", _("Utilities"))
        verbose_name = _("AppVersion")
        verbose_name_plural = _("AppVersions")

class PopAppVersion(AppVersion):
    class Meta:
        proxy = True
        app_label = string_with_title("utilities", _("Utilities"))
        verbose_name = _("PopAppVersion")
        verbose_name_plural = _("PopAppVersions")


class SubjectApplication(SubjectItem):
    class Meta:
        proxy = True
        app_label = string_with_title("utilities", _("Utilities"))
        verbose_name = _("Subject Item")
        verbose_name_plural = _("Subject Items")
