from django.db import models
from django.utils.translation import ugettext_lazy as _
from estorecore.models.base import EntityModel, DefaultManager
from estorecore.models.app import Application, CategorySubject
from estorecore.models.constants import MESSAGE_STATUS, PUSH_MESSAGE_ACTIONS, PUSH_MESSAGE_DISPLAY_AREAS
from estorecore.utils.storages import LocalFileSystemStorage


class Message(EntityModel):
    title = models.CharField(max_length=50, verbose_name=_('title'))
    content = models.TextField(max_length=1023, verbose_name=_('content'))
    link_url = models.URLField(max_length=255, null=True, blank=True, verbose_name=_('link URL'))
    icon_url = models.URLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('icon URL'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 64x64'))
    icon_path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/images/', null=True, blank=True, verbose_name=_('icon path'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 64x64'))
    client_id = models.CharField(max_length=60, null=True, blank=True, verbose_name=_('client id'))
    category = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('category'))
    invalid_before = models.DateTimeField(verbose_name=_('invalid before'))
    invalid_after = models.DateTimeField(verbose_name=_('invalid after'))
    short_message = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('short message'))
    locales = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('locales'))
    action = models.CharField(choices=PUSH_MESSAGE_ACTIONS.to_choices(), max_length=50, verbose_name=_('action'))
    value = models.CharField(max_length=255, verbose_name=_('value'))
    status = models.IntegerField(default=1, choices=MESSAGE_STATUS.to_choices(), verbose_name=_('status'))
    targets = models.CharField(max_length=409600, verbose_name=_('target'), null=True, blank=True)
    display_area = models.IntegerField(choices=PUSH_MESSAGE_DISPLAY_AREAS.to_choices(), verbose_name=_('display area'))
    extra_infos = models.CharField(max_length=1024, verbose_name=_('extra info'), null=True, blank=True)
    # ALTER TABLE `push_message` ADD COLUMN `extra_infos` varchar(1024) NULL;

    objects = DefaultManager()

    def __unicode__(self):
        return self.title

    def value_readable(self):
        if self.action in (PUSH_MESSAGE_ACTIONS.APP_DETAILES_PAGE, PUSH_MESSAGE_ACTIONS.SHORT_CUT_DETAIL_PAGE, \
                PUSH_MESSAGE_ACTIONS.SHORT_CUT_DOWNLOAD_APP, PUSH_MESSAGE_ACTIONS.DOWNLOAD_APP, \
                PUSH_MESSAGE_ACTIONS.DOWNLOADB, PUSH_MESSAGE_ACTIONS.LAUNCHB):
            try:
                app = Application.objects.get(pk=long(self.value))
                return _('App-%(app_id)s-%(app_name)s') % {'app_id': app.id, 'app_name': app.name}
            except:
                return _('App with id %(app_id)s does not exists') % {'app_id': self.value}
        elif self.action == PUSH_MESSAGE_ACTIONS.SUBJECT_INFO:
            try:
                subject = CategorySubject.objects.get(pk=long(self.value))
                return _('Subject-%(subject_id)s-%(subject_name)s') % {'subject_id': subject.id, 'subject_name': subject.name}
            except:
                return _('Subject with id %(subject_id)s does not exists') % {'subject_id': self.value}
        else:
            return self.value
    value_readable.short_description = _('value readable')

    def display_content(self):
        if len(self.content) > 30:
            return '%s...' % self.content[:30]
        return self.content
    display_content.short_description = _('content')

    class Meta:
        app_label = 'push'
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')