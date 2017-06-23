from django.utils.translation import ugettext as _

from estorecore.models.constants import APP_TAGS
from estorecore.models.app import CustomManager
from estoreoperation.utils import string_with_title
from estoreoperation.app.models import Application


class RiskApp(Application):
    objects = CustomManager({'tag': APP_TAGS.RISK})

    class Meta:
        proxy = True
        app_label = string_with_title("riskapps", _("Risk Apps"))
        verbose_name = _("Risk App")
        verbose_name_plural = _("Risk Apps")
