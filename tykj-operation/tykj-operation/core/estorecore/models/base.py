from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from estorecore.models.constants import SYNC_STATUS, REVIEW_STATUS, \
        RICHITEM_TYPE, STATS_TAGS


class EntityModel(models.Model):
    creator = models.ForeignKey(User, verbose_name=_("creator"))
    created_time = models.DateTimeField(verbose_name=_("created_time"))
    modifier = models.ForeignKey(User, verbose_name=_("modifier"), related_name="+")
    modified_time = models.DateTimeField(verbose_name=_("last modified"))
    published = models.BooleanField(default=False, verbose_name=_("published"))
    hided = models.BooleanField(default=False, verbose_name=_("hided"))
    sync_status = models.IntegerField(default=0, choices=SYNC_STATUS.to_choices(), verbose_name=_("sync status"))
    review_status = models.IntegerField(default=0, choices=REVIEW_STATUS.to_choices(), verbose_name=_('review status'))

    def modifier_name(self):
        if self.pk:
            return self.modifier.username
        return None
    modifier_name.short_description = _('modifier')

    def creator_name(self):
        if self.pk:
            return self.creator.username
        return None
    creator_name.short_description = _('creator')

    def delete(self):
        self.hided = 1
        self.sync_status = 0
        self.save()

    class Meta:
        abstract = True


class Ordered(EntityModel):
    order = models.IntegerField(null=True, blank=True, verbose_name=_('No.'))

    class Meta:
        abstract = True
        app_label = "list"


class RichItem(Ordered):
    type = models.IntegerField(choices=RICHITEM_TYPE.to_choices(), verbose_name=_('type'))
    attr = models.CharField(max_length=1023, verbose_name=_('attribute'))

    class Meta:
        abstract = True
        app_label = "list"


class Statistics(EntityModel):
    date = models.DateField(verbose_name=_('date'))
    month = models.DateField(null=True, blank=True, verbose_name=_('month'))
    year = models.IntegerField(null=True, blank=True, verbose_name=_('year'))
    tag = models.IntegerField(default=2, choices=STATS_TAGS.to_choices(), verbose_name=_('tag'))

    def save(self, *args, **kwargs):
        self.month = self.date
        self.year = self.date.year
        super(Statistics, self).save(args, kwargs)

    class Meta:
        abstract = True
        app_label = "stats"


class DefaultManager(models.Manager):

    def get_query_set(self):
        query_set = super(DefaultManager, self).get_query_set().filter(hided=False)
        return query_set.distinct('pk')


class CustomManager(DefaultManager):
    """
    Custom manager.
    options: queryset filter options
    """
    def __init__(self, options={}):
        self.options = options
        super(CustomManager, self).__init__()

    def get_query_set(self):
        query_set = super(CustomManager, self).get_query_set().filter(**self.options)
        return query_set


class StatsBaseModel(object):

    def click_count(self):
        if self.app and self.app.clicks_count:
            return self.app.clicks_count
        return 0
    click_count.short_description = _('clicks')

    def download_count(self):
        if self.app and self.app.downloads_count:
            return self.app.downloads_count
        return 0
    download_count.short_description = _('downloads')
