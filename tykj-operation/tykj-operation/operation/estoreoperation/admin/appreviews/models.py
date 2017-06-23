from django.utils.translation import ugettext as _

from estorecore.models.base import DefaultManager
from estoreoperation.utils import string_with_title
from estoreoperation.app.models import AppReview


class ApplicationReview(AppReview):

    objects = DefaultManager()

    class Meta:
        proxy = True
        app_label = string_with_title("appreviews", _("App Reviews"))
        verbose_name = _("App Review")
        verbose_name_plural = _("App Reviews")
