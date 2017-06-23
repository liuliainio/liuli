from django.db import models
from django.utils.translation import ugettext_lazy as _
from estorecore.models.constants import UPDATE_BTN_ACTIONS, REVIEW_STATUS
from estorecore.models.base import EntityModel, DefaultManager
from estorecore.utils.storages import LocalFileSystemStorage


class UpdateApp(EntityModel):
    package_name = models.CharField(max_length=255, verbose_name=_('package name'))
    version_name = models.CharField(max_length=255, verbose_name=_('version name'))
    source = models.CharField(max_length=255, verbose_name=_('source'))
    version_code = models.IntegerField(verbose_name=_('version code'))
    os = models.CharField(max_length=255, verbose_name=_('os'), null=True, blank=True)
    os_version = models.CharField(max_length=255, verbose_name=_('os version'), null=True, blank=True)
    resolution = models.CharField(max_length=255, verbose_name=_('resolution'), null=True, blank=True)
    cpu = models.CharField(max_length=255, verbose_name=_('cpu'), null=True, blank=True)
    model = models.CharField(max_length=255, verbose_name=_('model'), null=True, blank=True)
    rom = models.CharField(max_length=255, verbose_name=_('rom'), null=True, blank=True)
    package_hash = models.CharField(max_length=255, verbose_name=_('package hash'), null=True)
    # ALTER TABLE `update_updateapp` ADD COLUMN `package_hash` varchar(255) DEFAULT NULL;
    device = models.CharField(max_length=512, verbose_name=_('device'), null=True, blank=True)
    download_url = models.URLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('download URL'))
    download_path = models.FileField(storage=LocalFileSystemStorage(), null=True, blank=True, upload_to='static/apks/', verbose_name=_('download path'))
    is_force = models.BooleanField(default=False, verbose_name=_('is force'))
    is_auto = models.BooleanField(default=False, verbose_name=_('is auto'))
    is_patch = models.BooleanField(default=False, verbose_name=_('is patch'))
    channel_promote = models.BooleanField(default=False, verbose_name=_('channel promote'))
    title = models.CharField(max_length=255, verbose_name=_('title'))
    content_title = models.CharField(max_length=255, verbose_name=_('content title'))
    package_size = models.CharField(max_length=128, null=True, blank=True, verbose_name=_('package size'))
    change_log = models.TextField(verbose_name=_('change log'))

    objects = DefaultManager()

    def __unicode__(self):
        return self.package_name

    def save(self):
        if self.download_path and not self.package_size:
            self.package_size = self.download_path.size
        super(UpdateApp, self).save()

    def get_buttons(self):
        update_buttons = []
        for btn in self.buttons.all().filter(hided=False):
            update_buttons.append({
                    'action': btn.action,
                    'btn': btn.btn,
                    'order': btn.order,
                })
        return update_buttons

    class Meta:
        app_label = 'update'
        verbose_name = _('Update Application')
        verbose_name_plural = _('Update Applications')


class UpdateButton(EntityModel):
    update_app = models.ForeignKey(UpdateApp, related_name='buttons', verbose_name=_('update application'))
    action = models.CharField(choices=UPDATE_BTN_ACTIONS.to_choices(), max_length=255, verbose_name=_('action'))
    btn = models.CharField(max_length=255, verbose_name=_('button name'))
    order = models.IntegerField(verbose_name=_('order'))

    objects = DefaultManager()

    def __unicode__(self):
        return self.btn

    def save(self):
        self.review_status = REVIEW_STATUS.APPROVED
        self.published = True
        super(UpdateButton, self).save()

    class Meta:
        app_label = 'update'
        verbose_name = _('Update Button')
        verbose_name_plural = _('Update Buttons')
