import decimal
from django.db import models
from django.utils.translation import ugettext_lazy as _
from estoreoperation.utils import string_with_title
from estoreoperation.app.models import CategoryStats, ApplicationStats, AppVersionStats, CategoryFoucsImageStats, \
        CategorySubjectStats, CategoryRecommendAppStats, PreparedAppStats, BootAppStats, TopAppStats

DECIMAL_0 = decimal.Decimal(0)


class CategoryStatistics(CategoryStats):

    class Meta:
        proxy = True
        app_label = string_with_title("statistics", _("Statistics"))
        verbose_name = _('Category Stats')
        verbose_name_plural = _('Category Stats')


class ApplicationStatistics(ApplicationStats):

    class Meta:
        proxy = True
        app_label = string_with_title("statistics", _("Statistics"))
        verbose_name = _('Application Stats')
        verbose_name_plural = _('Application Stats')


class AppVersionStatistics(AppVersionStats):

    class Meta:
        proxy = True
        app_label = string_with_title("statistics", _("Statistics"))
        verbose_name = _('Application Version Stats')
        verbose_name_plural = _('Application Version Stats')


class CategoryFoucsImageStatistics(CategoryFoucsImageStats):

    class Meta:
        proxy = True
        app_label = string_with_title("statistics", _("Statistics"))
        verbose_name = _('Category Foucs Image Stats')
        verbose_name_plural = _('Category Foucs Image Stats')


class CategorySubjectStatistics(CategorySubjectStats):

    class Meta:
        proxy = True
        app_label = string_with_title("statistics", _("Statistics"))
        verbose_name = _('Category Subject Stats')
        verbose_name_plural = _('Category Subject Stats')


class CategoryRecommendAppStatistics(CategoryRecommendAppStats):

    class Meta:
        proxy = True
        app_label = string_with_title("statistics", _("Statistics"))
        verbose_name = _('Category Recommend Application Stats')
        verbose_name_plural = _('Category Recommend Application Stats')


class PreparedAppStatistics(PreparedAppStats):

    class Meta:
        proxy = True
        app_label = string_with_title("statistics", _("Statistics"))
        verbose_name = _('Prepared Application Stats')
        verbose_name_plural = _('Prepared Application Stats')


class BootAppStatistics(BootAppStats):

    class Meta:
        proxy = True
        app_label = string_with_title("statistics", _("Statistics"))
        verbose_name = _('Boot Application Stats')
        verbose_name_plural = _('Boot Application Stats')


class TopAppStatistics(TopAppStats):

    class Meta:
        proxy = True
        app_label = string_with_title("statistics", _("Statistics"))
        verbose_name = _('Top Application Stats')
        verbose_name_plural = _('Top Application Stats')
