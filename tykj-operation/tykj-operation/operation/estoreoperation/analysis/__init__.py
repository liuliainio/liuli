from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

reporting_items = [
        ('product_chart', 'product_reporting', _('Product Charts')),
        ('featured_chart', 'featured_reporting', _('Featured Charts')),
        ('topapps_chart', 'topapps_reporting', _('TopApps Charts')),
        ('category_chart', 'category_reporting', _('Category Charts')),
        ('download_chart', 'download_reporting', _('Download Page Charts')),
        ('topic_chart', 'topic_reporting', _('Topic Charts')),
        ('user_chart', 'user_reporting', _('User Data Charts')),
        ('search_chart', 'search_reporting', _('Search Charts')),
        ('detail_chart', 'detail_reporting', _('Detail Page Charts')),
        ('push_chart', 'push_reporting', _('Push Message Charts')),
    ]

# create reporting permissions
def _create_reporting_perms():
    ctype = ContentType.objects.get(model=User._meta.module_name, app_label=User._meta.app_label)

    for item in reporting_items:
        name = item[1]
        p = Permission.objects.get_or_create(
            codename="view_%s" % name,
            name="Can View %s" % name.replace('_', ' '),
            content_type=ctype
        )

#_create_reporting_perms()
