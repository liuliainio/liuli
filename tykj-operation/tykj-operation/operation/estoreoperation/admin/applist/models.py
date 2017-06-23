from django.db.models.base import ModelBase
from django.utils.translation import ugettext as _

from estorecore.admin.management import create_permission
from estorecore.models.constants import REVIEW_STATUS, APP_LIST_TYPES, RECOMMEND_TYPES
from estorecore.models.app import CustomManager, AppList, AppListItem, BELONGTOS
from estoreoperation.utils import string_with_title
from estoreoperation.app.models import CategorySubject, CategoryRecommendApp, TopApp, \
        PreparedApp, BootApp, KuWanItem


def applistitem_factory(class_s, app_list, model=AppListItem):

    def _get_meta(app_list):
        if app_list.list_type == APP_LIST_TYPES.BANNER:
            class Meta:
                proxy = True
                app_label = string_with_title("banner", _("Banner Recommend"))
                verbose_name = app_list.name
                verbose_name_plural = app_list.name
        else:
            class Meta:
                proxy = True
                app_label = string_with_title("applist", _("AppList"))
                verbose_name = app_list.name
                verbose_name_plural = app_list.name
        return Meta

    objects = CustomManager({'app_list': app_list})
    class_attrs = {
        'Meta': _get_meta(app_list),
        '__module__': __name__,
        'objects': objects
    }
    if app_list.list_type == APP_LIST_TYPES.BANNER:
        class_name = 'Banner%s%s' % (model.__name__, class_s)
    else:
        class_name = '%s%s' % (model.__name__, class_s)
    model_class = ModelBase(class_name, (model,), class_attrs)
    create_permission(model_class)
    return model_class


class NewestRecommendApp(CategoryRecommendApp):
    objects = CustomManager({'type': RECOMMEND_TYPES.NEWEST})

    class Meta:
        proxy = True
        app_label = string_with_title("applist", _("AppList"))
        verbose_name = _("Newest Recommendation")
        verbose_name_plural = _("Newest Recommendations")


class HottestRecommendApp(CategoryRecommendApp):
    objects = CustomManager({'type': RECOMMEND_TYPES.HOTTEST})

    class Meta:
        proxy = True
        app_label = string_with_title("applist", _("AppList"))
        verbose_name = _("Hottest Recommendation")
        verbose_name_plural = _("Hottest Recommendations")


class MatchestRecommendApp(CategoryRecommendApp):
    objects = CustomManager({'type': RECOMMEND_TYPES.MATCHEST})

    class Meta:
        proxy = True
        app_label = string_with_title("applist", _("AppList"))
        verbose_name = _("Matchest Recommendation")
        verbose_name_plural = _("Matchest Recommendations")


class HomeNewRecommendApp(CategoryRecommendApp):
    objects = CustomManager({'type': RECOMMEND_TYPES.HOME_NEW})

    class Meta:
        proxy = True
        app_label = string_with_title("applist", _("AppList"))
        verbose_name = _("HomeNew Recommendation")
        verbose_name_plural = _("HomeNew Recommendations")


class PreparedApp(PreparedApp):
    class Meta:
        proxy = True
        app_label = string_with_title("applist", _("AppList"))
        verbose_name = _('Prepared Application')
        verbose_name_plural = _('Prepared Applications')


class BootApp(BootApp):
    class Meta:
        proxy = True
        app_label = string_with_title("applist", _("AppList"))
        verbose_name = _('Boot Application')
        verbose_name_plural = _('Boot Applications')


class ApplicationTopApp(TopApp):
    objects = CustomManager({'app__category__name': _('Application')})

    class Meta:
        proxy = True
        app_label = string_with_title("applist", _("AppList"))
        verbose_name = _("Top Application")
        verbose_name_plural = _("Top Application")


class GameTopApp(TopApp):
    objects = CustomManager({'app__category__name': _('Game')})

    class Meta:
        proxy = True
        app_label = string_with_title("applist", _("AppList"))
        verbose_name = _("Top Game")
        verbose_name_plural = _("Top Game")


class ReadingTopApp(TopApp):
    objects = CustomManager({'app__category__name': _('Reading')})

    class Meta:
        proxy = True
        app_label = string_with_title("applist", _("AppList"))
        verbose_name = _("Top Reading")
        verbose_name_plural = _("Top Reading")


class MusicVideoTopApp(TopApp):
    objects = CustomManager({'app__category__name': _('Music & Video')})

    class Meta:
        proxy = True
        app_label = string_with_title("applist", _("AppList"))
        verbose_name = _("Top Music & Video")
        verbose_name_plural = _("Top Music & Video")


class TianYiKuWanItem(KuWanItem):
    class Meta:
        proxy = True
        app_label = string_with_title("applist", _("AppList"))
        verbose_name = _('TianYi KuWan')
        verbose_name_plural = _('TianYi KuWan')
