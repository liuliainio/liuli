from django.utils.translation import ugettext as _

from estoreoperation.utils import string_with_title
from estoreoperation.app.models import Category


class AppCategory(Category):

    class Meta:
        proxy = True
        app_label = string_with_title("category", _("App Category"))
        verbose_name = _("App Category")
        verbose_name_plural = _("App Categorys")
