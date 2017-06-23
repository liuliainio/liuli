from django.db import models
from django.utils.translation import ugettext_lazy as _
from estoreoperation.utils import string_with_title
from estorecore.models.base import Ordered, DefaultManager
from estorecore.models.constants import SEARCH_TREND
from estorecore.models.app import Application

class SearchKeyword(Ordered):
    keyword = models.CharField(max_length=255, unique=True, verbose_name=_('keyword'))
    search_count = models.BigIntegerField(default=0, verbose_name=_('search count'))
    search_trend = models.IntegerField(default=1, choices=SEARCH_TREND.to_choices(), verbose_name=_('search trend'))
    # ALTER TABLE `search_searchkeyword` ADD COLUMN `search_trend` int(11) NOT NULL DEFAULT 1;

    objects = DefaultManager()

    def __unicode__(self):
        return self.keyword

    def delete(self):
        '''
        default delete action is to hide a app
        but this function is different from others
        it is a real delete action
        '''
        models.Model.delete(self)

    class Meta:
        app_label = string_with_title("search", _("Search"))
        verbose_name = _('Search Keyword label')
        verbose_name_plural = _('Search Keywords label')

class KeywordLocation(Ordered):
    keyword = models.CharField(max_length=255, verbose_name=_('keyword'))
    app = models.ForeignKey(Application, verbose_name=_('application'))
    location = models.BigIntegerField(default=1, verbose_name=_('location'))

    def __unicode__(self):
        return self.keyword

    class Meta:
        app_label = string_with_title("search", _("Search"))
        verbose_name = _('Keyword Location')
        verbose_name_plural = _('Keywords Location')
