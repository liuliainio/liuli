from django.utils.translation import ugettext as _

from estorecore.models.constants import APP_SOURCES
from estorecore.models.app import CustomManager
from estoreoperation.utils import string_with_title
from estoreoperation.app.models import Application, AppMaskOff
from estorecore.models.constants import REVIEW_STATUS


class ManuallyAddedApp(Application):
    objects = CustomManager({'source': APP_SOURCES.MANUAL, 'review_status': REVIEW_STATUS.NOT_REVIEWED})

    class Meta:
        proxy = True
        app_label = string_with_title("newapps", _("New Apps"))
        verbose_name = _("Manually Added")
        verbose_name_plural = _("Manually Added")


class AutoCrawledApp(Application):
    objects = CustomManager({'source__gte': APP_SOURCES.CRAWLED, 'review_status': REVIEW_STATUS.NOT_REVIEWED})

    class Meta:
        proxy = True
        app_label = string_with_title("newapps", _("New Apps"))
        verbose_name = _("Auto Crawled")
        verbose_name_plural = _("Auto Crawled")


class DevUploadedApp(Application):
    objects = CustomManager({'source': APP_SOURCES.DEV_UPLOAD, 'review_status': REVIEW_STATUS.NOT_REVIEWED})

    class Meta:
        proxy = True
        app_label = string_with_title("newapps", _("New Apps"))
        verbose_name = _("Developer Uploaded")
        verbose_name_plural = _("Developer Uploaded")


class AutoMaskOffApp(AppMaskOff):
    class Meta:
        proxy = True
        app_label = string_with_title("newapps", _("New Apps"))
        verbose_name = _("auto mask off app")
        verbose_name_plural = _("auto mask off app")
