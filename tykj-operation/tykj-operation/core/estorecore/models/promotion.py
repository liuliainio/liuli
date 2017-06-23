from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from estorecore.models.base import EntityModel, RichItem, Ordered, DefaultManager
from estorecore.models.constants import ACTIVITY_TAGS, ACTIVITY_STATUS, LOCAL_ENTRY_ACTION, LOCAL_ENTRY_PARAMETER
from estorecore.utils.storages import LocalFileSystemStorage
from django.contrib.auth.models import Group

class Activity(RichItem):
    title = models.CharField(max_length=255, verbose_name=_('title'))
    start_date = models.DateTimeField(verbose_name=_('start date'))
    end_date = models.DateTimeField(verbose_name=_('end date'))
    description = models.TextField(max_length=1023, verbose_name=_('description'))
    pub_date = models.DateTimeField(verbose_name=_('publish date'))
    icon_url = models.URLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('icon URL'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 120x144'))
    icon_path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/images/', verbose_name=_('icon path'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 120x144'))
    large_icon_url = models.URLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('large icon URL'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 480x200'))
    large_icon_path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/zimages/', max_length=255, verbose_name=_('large icon path'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 480x200'), null=True, blank=True)
    status = models.IntegerField(default=0, choices=ACTIVITY_STATUS.to_choices(), verbose_name=_('status'))
    tag = models.IntegerField(choices=ACTIVITY_TAGS.to_choices(), verbose_name=_('tag'))
    group = models.ForeignKey(Group, verbose_name=_('user group'),null=True, blank=True, editable=False)

    objects = DefaultManager()

    def save(self):
        if self.icon_path:
            self.icon_path.name = smart_str(self.icon_path.name)
        super(Activity, self).save()

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'promotion'
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')


class LoginPicture(RichItem):
    name = models.CharField(max_length=255, verbose_name=_('picture name'))
    url = models.URLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('picture URL'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 320x480'))
    path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/images/', verbose_name=_('picture path'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 320x480'))
    start_date = models.DateTimeField(verbose_name=_('start date'))
    end_date = models.DateTimeField(verbose_name=_('end date'))
    is_default = models.BooleanField(verbose_name=_('is default'))
    search_keyword = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('search keyword'))
    home_banner = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Home Banner'))
    group = models.ForeignKey(Group, verbose_name=_('user group'),null=True, blank=True, editable=False)

    objects = DefaultManager()

    def save(self):
        if self.path:
            self.path.name = smart_str(self.path.name)
        super(LoginPicture, self).save()

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'promotion'
        verbose_name = _('Login Picture')
        verbose_name_plural = _('Login Pictures')


class Feedback(models.Model):
    user_id = models.IntegerField(_('user ID'))
    content = models.TextField(max_length=1023, verbose_name=_('content'))
    created_time = models.DateTimeField(_('created time'))
    # alter table promotion_feedback add column `source` varchar(255) null;
    source = models.CharField(max_length=255, verbose_name=_('source'), default='')
    # alter table promotion_feedback add column `extras` varchar(512) null;
    extras = models.CharField(max_length=512, verbose_name=_('extras'), default='')
    # alter table promotion_feedback add column `app_key` varchar(255) not null;
    app_key = models.CharField(max_length=255, verbose_name=_('app key'))

    def __unicode__(self):
        return self.content

    class Meta:
        app_label = 'promotion'
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedbacks')


class LocalEntry(Ordered):
    name = models.CharField(max_length=255, verbose_name=_('title'))
    icon_path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/images/', verbose_name=_('icon path'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 120x60'))
    action = models.CharField(max_length=64, verbose_name=_('action'), choices=LOCAL_ENTRY_ACTION.to_choices())
    value = models.CharField(max_length=256, verbose_name=_('value'))
    parameter = models.CharField(max_length=64, verbose_name=_('parameter'), choices=LOCAL_ENTRY_PARAMETER.to_choices())
    condition = models.CharField(max_length=128, verbose_name=_('condition'), null=True, blank=True)
    objects = DefaultManager()

    def save(self):
        if self.icon_path:
            self.icon_path.name = smart_str(self.icon_path.name)
        super(LocalEntry, self).save()

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'promotion'
        verbose_name = _('LocalEntry')
        verbose_name_plural = _('LocalEntries')
