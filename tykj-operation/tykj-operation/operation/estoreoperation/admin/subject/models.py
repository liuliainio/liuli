from django.utils.translation import ugettext as _
from estoreoperation.utils import string_with_title
from estoreoperation.promotion.models import Activity
from estoreoperation.app.models import CategorySubject


class AppSubject(CategorySubject):
    class Meta:
        proxy = True
        app_label = string_with_title("subject", _("Subject Management"))
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjects")


class Activity(Activity):
    class Meta:
        proxy = True
        app_label = string_with_title("subject", _("Subject Management"))
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")