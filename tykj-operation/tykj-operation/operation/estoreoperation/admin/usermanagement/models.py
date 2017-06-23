from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _

from estoreoperation.utils import string_with_title


class GroupManagement(Group):

    class Meta:
        proxy = True
        app_label = string_with_title("usermanagement", _("User Management"))
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")


class UserManagement(User):

    class Meta:
        proxy = True
        app_label = string_with_title("usermanagement", _("User Management"))
        verbose_name = _("User")
        verbose_name_plural = _("Users")
