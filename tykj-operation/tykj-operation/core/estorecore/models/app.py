#! -*- coding: utf-8 -*-
import os
import logging
import decimal
from django.db import models
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from estorecore.utils import parse_url, string_with_title
from estorecore.utils.watermark import watermark
from estorecore.utils.storages import LocalFileSystemStorage, extract_apk_info
from estorecore.models.base import EntityModel, Ordered, RichItem, Statistics, StatsBaseModel, CustomManager
from estorecore.models.constants import BELONGTOS, CATEGORY_LEVELS, APP_SOURCES, APP_TAGS, RICHITEM_TYPE, \
    RECOMMEND_TYPES, APP_RATES, SYNC_STATUS, REVIEW_STATUS, BANNER_IMAGE_AREAS, STATS_TAGS, APP_LIST_TYPES,\
    TIANYI_STATUS, TIANYI_CHARGEMODE, KUWAN_LIST_TYPES, REVIEWED_DESC_PREVIEW_STATUS, TIANYI_PAY_TYPES, SUBJECT_TML
from smart_selects.db_fields import ChainedForeignKey
from estorecore.models.fields import BtnURLField
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group


DECIMAL_0 = decimal.Decimal(0)
POSTFIX_REG = r'_hot\.|_top\.|_charges\.|_recommend\.'

logger = logging.getLogger('estoreoperation')


def _add_watermark_postfix(path):
    if '_marked' not in path:
        path = path.replace('.', '_marked.') if '.' in path \
            else '%s_marked' % path
    return path


def _get_icon_file_path(icon_path):
    icon_path_name = icon_path.name
    if 'img/full' in icon_path_name:
        return os.path.join('/mnt/ctappstore1', icon_path_name)
    elif 'data/app_files' in icon_path_name or 'data/user_files' in icon_path_name:
        return os.path.join('/mnt/ctappstore2/vol1', icon_path_name.replace('img/', ''))
    else:
        return icon_path.path


class LastImportAppID(models.Model):
    last_import_app_id = models.BigIntegerField()
    last_import_time = models.DateTimeField()

    class Meta:
        app_label = 'app'


""" META DATA """
class Category(Ordered):
    name = models.CharField(max_length=255, verbose_name=_('category name'))
    description = models.TextField(max_length=4096, verbose_name=_('description'))
    icon_url = models.URLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('icon URL'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 64x64'))
    icon_path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/images/', verbose_name=_('icon path'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 64x64'))
    level = models.IntegerField(choices=CATEGORY_LEVELS.to_choices(), verbose_name=_('level'))
    # parent_category null means top level
    parent_category = models.ForeignKey('self', related_name='children', limit_choices_to={'level__exact': CATEGORY_LEVELS.CATEGORY}, \
            null=True, blank=True, default=None, verbose_name=_('parent category'))

    objects = CustomManager()

    def app_counts(self):
        if self.pk:
            if self.parent_category is None:
                return self.total_apps.filter(hided=False).count()
            else:
                return self.apps.filter(hided=False).count()
        return 0
    app_counts.short_description = _('application count')

    def click_count(self):
        if self.pk:
            result = self.stats.values('clicks').annotate(clicks_count=models.Sum('clicks'))
            if result:
                return result[0]['clicks_count']
        return 0
    click_count.short_description = _('clicks')
    click_count.admin_order_field = 'clicks_count'

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'app'
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        unique_together = ("name", "level")


class AppVersion(EntityModel, StatsBaseModel):
    t_status = models.IntegerField(default=0, choices=TIANYI_STATUS.to_choices(), verbose_name=_("tianyi status"))
    app = models.ForeignKey("Application", related_name='versions', verbose_name=_('application'))
    version = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('version'))
    version_code = models.IntegerField(verbose_name=_('version code'), null=True, blank=True)
    source = models.IntegerField(choices=APP_SOURCES.to_choices(), verbose_name=_('source'))
    developer = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('developer'))
    description = models.TextField(max_length=4096, verbose_name=_('description'))
    price = models.DecimalField(default=DECIMAL_0, max_digits=25, decimal_places=5, verbose_name=_('price'))
    pub_date = models.DateTimeField(verbose_name=_('publish date'))
    icon_url = BtnURLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('icon URL'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 72x72'))
    icon_path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/images/', null=True, blank=True, verbose_name=_('icon path'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 72x72'))
    download_url = models.URLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('download URL'))
    download_path = models.FileField(storage=LocalFileSystemStorage(), upload_to='static/apks/', verbose_name=_('download path'))
    size = models.BigIntegerField(default=0, null=True, blank=True, verbose_name=_('size'))
    package_hash = models.CharField(max_length=255, verbose_name=_('package hash'), null=True, blank=True)
    min_sdk_version = models.IntegerField(null=True, blank=True, verbose_name=_('min sdk version'))
    reviewed_desc_preview = models.BooleanField(default=False, verbose_name=_("reviewed desc preview"))
    #alter table appversion add column external_download_url varchar(2048) default null
    external_download_url = models.CharField(max_length=2048, verbose_name=_('external app download url'), null=True, blank=True)
    labels = models.CharField(max_length=512, verbose_name=_('labels'), null=True, blank=True)
    update_note = models.TextField(max_length=4096, null=True, blank=True, verbose_name=_('update_note'))
    tencent_safe = models.SmallIntegerField(blank=True, null=True, verbose_name=_('tencent safe'))
    objects = CustomManager()

    def save(self, save_apk_info=None):
        old_obj = AppVersion.objects.get(pk__exact=self.id) if self.pk else None
        self.download_path.name = smart_str(self.download_path.name)
        super(AppVersion, self).save()
        if save_apk_info is None:
            if not old_obj or old_obj.download_path != self.download_path:
                self._set_apk_info()
        elif save_apk_info:
            self._set_apk_info()

        if self.app.versions_count != self.app.versions.count():
            self.app.versions_count = self.app.versions.count()
        if not self.app.current_version:
            self.app.current_version = self
        if self.app.current_version and self.id == self.app.current_version.id \
                and self.app.sync_status == SYNC_STATUS.SYNCED:
            self.app.sync_status = 0

        if not old_obj or  old_obj.reviewed_desc_preview != self.reviewed_desc_preview:
            reviewed_versions = AppVersion.objects.filter(app=self.app, reviewed_desc_preview=1).order_by('-version_code')
            if reviewed_versions.count() == 0:
                self.app.reviewed_desc_preview_status = 0
            elif reviewed_versions[0] == self.app.current_version:
                self.app.reviewed_desc_preview_status = 2
            else:
                self.app.reviewed_desc_preview_status = 1

        self.app.save()

    def _set_apk_info(self):
        apk_info = extract_apk_info(self, with_apk_sign=True)
        self.size = apk_info.get('size', 0)
        self.version = apk_info.get('version_name', None)
        self.version_code = apk_info.get('version_code', None)
        self.package_hash = apk_info.get('package_hash', None)
        self.min_sdk_version = apk_info.get('min_sdk_version', None)
        icon = apk_info.get('icon', None)
        if icon:
            self.icon_path.save(icon[0], icon[1])

        if not self.app.package_name:
            self.app.package_name = apk_info.get('package_name', None)
        self.app.package_sig = apk_info.get('package_sign', None)
        self.save(save_apk_info=False)

    def app_version(self):
        if self.pk:
            return '%s - v%s' % (self.app.name, self.version)
        return self.version
    app_version.short_description = _('application version')

    def source_name(self):
        source_dict = APP_SOURCES.to_dict()
        if self.source in source_dict:
            return source_dict[self.source]
        else:
            return _('Unknown')
    source_name.short_description = _('source')
    source_name.admin_order_field = 'source'

    def rate(self):
        if self.pk and self.stats.count() > 0:
            return self.stats.all()[0].rate
        return 0
    rate.short_description = _('rating')

    def icon_urls(self):
        preview_icon_urls = [icon.url or parse_url(icon.path.url) for icon in self.preview_icon_urls.all() if not icon.hided]
        return ','.join(preview_icon_urls)

    def __unicode__(self):
        return '%s - %s' % (self.version, self.get_source_display())

    class Meta:
        app_label = 'app'
        verbose_name = _('Application Version')
        verbose_name_plural = _('Application Versions')


class PreviewIcon(Ordered):
    appversion = models.ForeignKey(AppVersion, related_name="preview_icon_urls", verbose_name=_('application version'))
    url = BtnURLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('icon URL'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 320x480'))
    path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/images/', verbose_name=_('icon path'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 320x480'))
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('icon title'))

    def save(self):
        self.path.name = smart_str(self.path.name)
        # for PreviewIcon , pass and published by default
        self.review_status = REVIEW_STATUS.APPROVED
        self.published = True
        # the name of path maybe changed by system when save
        # so need to save before changing the value of title
        super(PreviewIcon, self).save()
        self.title = self.path.name.split('/')[-1] or self.url.split('/')[-1]
        super(PreviewIcon, self).save()
        version = self.appversion.app.versions.all().order_by('-version_code')[0]
        self.appversion.app.has_icon = True if version.preview_icon_urls.count() > 0 else False
        self.appversion.app.save()

    def __unicode__(self):
        return self.url

    class Meta:
        app_label = 'app'
        verbose_name = _('Preview Icon')
        verbose_name_plural = _('Preview Icons')


class Application(Ordered):
    t_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name=_('tianyi id'))
    t_status = models.IntegerField(default=0, choices=TIANYI_STATUS.to_choices(), verbose_name=_("tianyi status"))
    t_chargemode = models.IntegerField(default=0, choices=TIANYI_CHARGEMODE.to_choices(), verbose_name=_("tianyi charge mode"))
    name = models.CharField(max_length=255, verbose_name=_('name'))
    package_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('package name'))
    package_sig = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('package signature'))
    current_version = models.ForeignKey(AppVersion, related_name='+', null=True, blank=True, default=None, verbose_name=_('current version'))
    prev_version = models.ForeignKey(AppVersion, related_name='+', null=True, blank=True, default=None, verbose_name=_('previous version'))
    category = models.ForeignKey(Category, related_name="total_apps", limit_choices_to={'level__exact': CATEGORY_LEVELS.CATEGORY}, verbose_name=_('category'))
    sub_category = ChainedForeignKey(Category, related_name="apps", verbose_name=_('sub category'), \
            chained_field="category", chained_model_field="parent_category", show_all=False, auto_choose=True)
    sub_category.sub_category_filter = True
    tag = models.IntegerField(choices=sorted(list(APP_TAGS.to_choices())), verbose_name=_('application tag'))
    has_icon = models.BooleanField(default=False, verbose_name=_('has preview'))
    versions_count = models.IntegerField(default=0, verbose_name=_('versions'))
    source = models.IntegerField(default=APP_SOURCES.MANUAL, verbose_name=_('source'))
    rate = models.DecimalField(default=DECIMAL_0, choices=APP_RATES, max_digits=25, decimal_places=1, verbose_name=_('rate'))
    clicks_count = models.BigIntegerField(default=0, verbose_name=_('clicks'))
    downloads_count = models.BigIntegerField(default=0, verbose_name=_('downloads'))
    reviews_count = models.BigIntegerField(default=0, verbose_name=_('reviews'))
    price = models.DecimalField(default=DECIMAL_0, max_digits=25, decimal_places=5, verbose_name=_('price'))
    current_version_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('current version'))
    # ALTER TABLE `app_application` ADD COLUMN `label` varchar(4096) NULL;
    label = models.CharField(max_length=4096, null=True, blank=True, verbose_name=_('app label'))
    # ALTER TABLE `app_application` ADD COLUMN `blocked_devices` varchar(4096) NULL;
    blocked_devices = models.TextField(max_length=4096, null=True, blank=True, verbose_name=_('blocked devices'), \
        help_text=_('Please use en separator when split device name.'))
    # ALTER TABLE `app_application` ADD COLUMN `reviewed_desc_preview_status` int(11) NOT NULL DEFAULT 0;
    reviewed_desc_preview_status = models.IntegerField(default=0, choices=REVIEWED_DESC_PREVIEW_STATUS.to_choices(), verbose_name=_('reviewed desc preview status'))
    # ALTER TABLE `app_application` ADD COLUMN `is_copycat` tinyint(1) NOT NULL default 0;
    is_copycat = models.BooleanField(default=False, verbose_name=_("copycat"))
    # ALTER TABLE `app_application` ADD COLUMN `t_paytype` int(11) NOT NULL default 0;
    t_paytype = models.IntegerField(default=0, choices=TIANYI_PAY_TYPES.to_choices(), verbose_name=_("tianyi pay types"))
    unpublished_reason = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('unpublished reason'))

    objects = CustomManager()

    def save(self):
        # add watermark for app
        # old_tag = -1 when create new app
        old_tag = -1 if not self.pk else Application.objects.get(pk__exact=self.id).tag
        if old_tag != self.tag and self.current_version and self.current_version.icon_path:
            # TODO: remove old tag icon file
            if self.tag >= APP_TAGS.TOP:
                try:
                    icon_real_path = _get_icon_file_path(self.current_version.icon_path)
                    new_icon_filename = _add_watermark_postfix(icon_real_path)
                    img = watermark(icon_real_path, APP_TAGS.get_key(self.tag).lower() + '.png')
                    img.save(new_icon_filename, quality=95)
                except Exception, e:
                    logger.error('Add watermark failed, error: %s' % e)
                new_icon_path = _add_watermark_postfix(self.current_version.icon_path.name)
            elif self.tag < APP_TAGS.TOP and old_tag >= APP_TAGS.TOP:
                new_icon_path = self.current_version.icon_path.name.replace('_marked', '')
            else:
                new_icon_path = None
            # save new icon path
            if new_icon_path is not None:
                self.current_version.icon_path = new_icon_path
                self.current_version.save(save_apk_info=False)

        if self.pk and self.current_version:
            self.source = self.current_version.source
            self.price = self.current_version.price
        else:
            self.source = APP_SOURCES.MANUAL
            self.price = DECIMAL_0

        old_obj = Application.objects.get(pk__exact=self.id) if self.pk else None
        if (not old_obj and self.current_version) or (old_obj and self.current_version != old_obj.current_version):
            self.current_version_name = self.current_version.version
        super(Application, self).save()

    def full_category(self):
        return '%s-%s' % (self.category, self.sub_category)
    full_category.short_description = _('full category')

    def sub_category_name(self):
        return self.sub_category
    sub_category_name.short_description = _('sub category')

    def source_name(self):
        source_dict = APP_SOURCES.to_dict()
        if self.source in source_dict:
            return source_dict[self.source]
        else:
            return _('Unknown')
    source_name.short_description = _('source')
    source_name.admin_order_field = 'source'

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'app'
        verbose_name = _('Application')
        verbose_name_plural = _('Applications')


class CategorySubject(Ordered):
    name = models.CharField(max_length=255, verbose_name=_('name'))
    sub_title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('sub title'))
    clicks_count = models.IntegerField(default=0, verbose_name=_('clicks'))
    description = models.TextField(max_length=4096, verbose_name=_('description'))
    pub_date = models.DateTimeField(verbose_name=_('publish date'))
    icon_url = models.URLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('icon URL'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 68x68'))
    icon_path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/images/', verbose_name=_('icon path'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 68x68'))
    large_icon_url = models.URLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('large icon URL'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 480x200'))
    large_icon_path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/zimages/', max_length=255, verbose_name=_('large icon path'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 480x200'), null=True, blank=True)
    subject_tml = models.IntegerField(choices=SUBJECT_TML.to_choices(), verbose_name=_('subject template'), \
            help_text=_('Please select client subject display template'), default=SUBJECT_TML.NOT_SET, blank=True)
    objects = CustomManager()

    def __unicode__(self):
        return self.name

    def save(self):
        if self.icon_path:
            self.icon_path.name = smart_str(self.icon_path.name)
        super(CategorySubject, self).save()
        SubjectItem.objects.filter(subject__id=self.pk).update(sync_status=0)

    class Meta:
        app_label = 'app'
        verbose_name = _('Category Subject')
        verbose_name_plural = _('Category Subjects')


class CategoryFoucsImage(RichItem):
    category = models.ForeignKey(Category, limit_choices_to={'level__exact': CATEGORY_LEVELS.CATEGORY}, null=True, blank=True, verbose_name=_('category'))
    recommend_type = models.IntegerField(choices=RECOMMEND_TYPES.to_choices(), null=True, blank=True, verbose_name=_('recommend type'))
    pub_date = models.DateTimeField(verbose_name=_('publish date'))
    icon_url = models.URLField(
        verify_exists=False,
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('icon URL'),
        help_text=_('Please upload JPEG, PNG, GIF files, size: 480x210')
    )
    icon_path = models.ImageField(
        storage=LocalFileSystemStorage(),
        upload_to='static/images/',
        verbose_name=_('icon path'),
        help_text=_('Please upload JPEG, PNG, GIF files, size: 480x210')
    )
    area = models.IntegerField(choices=BANNER_IMAGE_AREAS.to_choices(), verbose_name=_('area'))
    group = models.ForeignKey(Group, verbose_name=_('user group'), null=True, blank=True, editable=False)
    cooperate_list_id = models.CharField(
        max_length=256,
        verbose_name=_('cooperate_list_id'),
        blank=True,
        null=True,
        help_text=_('Examples: tianyireading, lovemusic, lovegame, loveanimation, tianyishixun, liuliangbao')
    )
    cooperate_list_name = models.CharField(
        max_length=256,
        verbose_name=_('cooperate_list_name'),
        blank=True,
        null=True,
        help_text=_(u'Examples: 天翼阅读, 爱音乐, 爱游戏, 爱动漫, 天翼视讯, 流量宝专区')
    )
    objects = CustomManager()

    def __unicode__(self):
        return BANNER_IMAGE_AREAS.to_dict()[self.area]._proxy____unicode_cast()

    def save(self):
        if self.icon_path:
            self.icon_path.name = smart_str(self.icon_path.name)
        super(CategoryFoucsImage, self).save()

    def attr_readable(self):
        if self.type and self.attr:
            if self.type == RICHITEM_TYPE.APP_DETAILES_PAGE:
                try:
                    app = Application.objects.get(id=long(self.attr))
                    return _('App-%(app_id)s-%(app_name)s') % {'app_id': app.id, 'app_name': app.name}
                except:
                    return _('App with id %(app_id)s does not exists') % {'app_id': self.attr}
            elif self.type == RICHITEM_TYPE.SUBJECT_INFO:
                try:
                    subject = CategorySubject.objects.get(id=long(self.attr))
                    return _('Subject-%(subject_id)s-%(subject_name)s') % {'subject_id': subject.id, 'subject_name': subject.name}
                except:
                    return _('Subject with id %(subject_id)s does not exists') % {'subject_id': self.attr}
        return self.attr
    attr_readable.short_description = _('attr readable')

    def click_count(self):
        if self.pk:
            result = self.stats.values('clicks').annotate(clicks_count=models.Sum('clicks'))
            if result:
                return result[0]['clicks_count']
        return 0
    click_count.short_description = _('clicks')
    click_count.admin_order_field = 'clicks_count'

    class Meta:
        app_label = 'app'
        verbose_name = _('Category Foucs Image')
        verbose_name_plural = _('Category Foucs Images')


class ExternalApp():

    def __unicode__(self):
        if self.app:
            return self.app.name
        elif self.title:
            return self.title
        else:
            return str(self.id)

    def app_id(self):
        return self.app.id
    app_id.short_description = _('app ID')

    def source(self):
        if self.pk:
            return self.app.source_name()
        return ''
    source.short_description = _('source')

    def version(self):
        if self.pk:
            return self.app.current_version.version
        return ''
    version.short_description = _('current version')

    def versions_count(self):
        if self.pk:
            return self.app.versions_count
        return 0
    versions_count.short_description = _('versions')

    def has_icon(self):
        if self.pk:
            return self.app.has_icon
        return False
    has_icon.short_description = _('has preview')
    has_icon.boolean = True

    def reviews_count(self):
        if self.pk:
            return self.app.reviews_count
        return 0
    reviews_count.short_description = _('reviews')

    def rate(self):
        if self.pk:
            return self.app.rate
        return 0
    rate.short_description = _('rating')

    def full_category(self):
        if self.pk:
            return self.app.full_category()
        return ''
    full_category.short_description = _('full category')


class SubjectItem(Ordered):
    subject = models.ForeignKey(CategorySubject, related_name='items', verbose_name=_('subject'))
    title = models.CharField(max_length=255, verbose_name=_('title'))
    description = models.TextField(max_length=4096, verbose_name=_('description'))
    icon_url = models.URLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('icon URL'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 480x210'))
    icon_path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/images/', null=True, blank=True, verbose_name=_('icon path'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 480x210'))

    objects = CustomManager()

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'app'
        verbose_name = _('Subject Item')
        verbose_name_plural = _('Subject Items')


class SubjectApp(models.Model):
    order = models.IntegerField(null=True, blank=True, verbose_name=_('No.'))
    app = models.ForeignKey(Application, limit_choices_to={'review_status__exact': 1, 'published': 1}, related_name='item', verbose_name=_('application'))
    subject_item = models.ForeignKey(SubjectItem, related_name='apps', verbose_name=_('subject item'))

    def __unicode__(self):
        return self.app.name

    class Meta:
        app_label = 'app'
        verbose_name = _('Subject Application')
        verbose_name_plural = _('Subject Applications')


class KuWanItem(Ordered):
    title = models.CharField(max_length=255, verbose_name=_('title'))
    description = models.TextField(max_length=4096, verbose_name=_('description'))
    price = models.DecimalField(default=DECIMAL_0, max_digits=25, decimal_places=5, verbose_name=_('price'))
    icon_url = models.URLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('icon URL'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 135x231'))
    icon_path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/images/', null=True, blank=True, verbose_name=_('icon path'), \
            help_text=_('Please upload JPEG, PNG, GIF files, size: 135x231'))
    list_type = models.IntegerField(choices=KUWAN_LIST_TYPES.to_choices(), verbose_name=_('list type'), \
            help_text=_('need to be the same with huawei kuwan type'))
    t_id = models.IntegerField(verbose_name=_('tianyi kuwan id'), help_text=_('need to be the same with huaWei platform kuwan item id'))
    # ALTER TABLE `app_kuwanitem` ADD COLUMN `list_type` int(11) NOT NULL, ADD COLUMN `t_id` int(11) NOT NULL;
    # ALTER TABLE estore.app_kuwanitem MODIFY COLUMN title VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
    # ALTER TABLE estore.app_kuwanitem MODIFY COLUMN description longtext CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
    # ALTER TABLE estore.app_kuwanitem MODIFY COLUMN icon_url VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

    objects = CustomManager()

    def __unicode__(self):
        return self.title

    def save(self):
        if self.icon_path:
            self.icon_path.name = smart_str(self.icon_path.name)
        super(KuWanItem, self).save()

    class Meta:
        app_label = 'app'
        verbose_name = _('TianYi KuWan')
        verbose_name_plural = _('TianYi KuWan')


class KuWanApp(models.Model):
    order = models.IntegerField(null=True, blank=True, verbose_name=_('No.'))
    app = models.ForeignKey(Application, limit_choices_to={'review_status__exact': 1, 'published': 1}, related_name='kuwan_item', verbose_name=_('application'))
    kuwan_item = models.ForeignKey(KuWanItem, related_name='apps', verbose_name=_('TianYi KuWan'))

    def __unicode__(self):
        return self.app.name

    class Meta:
        app_label = 'app'
        verbose_name = _('KuWan Application')
        verbose_name_plural = _('KuWan Applications')


class CategoryRecommendApp(Ordered, ExternalApp, StatsBaseModel):
    app = models.ForeignKey(Application, limit_choices_to={'review_status__exact': 1, 'published': 1}, verbose_name=_('application'))
    type = models.IntegerField(choices=RECOMMEND_TYPES.to_choices(), verbose_name=_('type'))
    pub_date = models.DateTimeField(verbose_name=_('publish date'))
    group = models.ForeignKey(Group, verbose_name=_('user group'),null=True, blank=True, editable=False)
    objects = CustomManager()

    class Meta:
        app_label = 'app'
        verbose_name = _('Category Recommend Application')
        verbose_name_plural = _('Category Recommend Applications')


class PreparedApp(Ordered, ExternalApp, StatsBaseModel):
    app = models.ForeignKey(Application, limit_choices_to={'review_status__exact': 1, 'published': 1}, verbose_name=_('application'))

    objects = CustomManager()

    class Meta:
        app_label = 'app'
        verbose_name = _('Prepared Application')
        verbose_name_plural = _('Prepared Applications')


class BootApp(Ordered, ExternalApp, StatsBaseModel):
    app = models.ForeignKey(Application, limit_choices_to={'review_status__exact': 1, 'published': 1}, verbose_name=_('application'))
    boot_app_type = models.CharField(max_length=255, verbose_name=_('boot app type'))
    # ALTER TABLE `app_bootapp` ADD COLUMN `boot_app_type` varchar(255) NOT NULL;

    objects = CustomManager()

    class Meta:
        app_label = 'app'
        verbose_name = _('Boot Application')
        verbose_name_plural = _('Boot Applications')


class TopApp(Ordered, ExternalApp, StatsBaseModel):
    app = models.ForeignKey(Application, limit_choices_to={'review_status__exact': 1, 'published': 1}, verbose_name=_('application'))
    short_desc = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('short description'))
    objects = CustomManager()

    class Meta:
        app_label = 'app'
        verbose_name = _('Top Application')
        verbose_name_plural = _('Top Applications')


class AppList(EntityModel):
    name = models.CharField(max_length=255, verbose_name=_('app list name'))
    codename = models.CharField(max_length=255, verbose_name=_('code name'))
    belong_to = models.IntegerField(choices=BELONGTOS.to_choices(), verbose_name=_('belong to'))
    list_type = models.IntegerField(default=0, choices=APP_LIST_TYPES.to_choices(), verbose_name=_('list type'))
    objects = CustomManager()

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'app'
        verbose_name = _('AppList')
        verbose_name_plural = _('AppList')
        unique_together = ("codename", "belong_to")


class AppListItem(RichItem, ExternalApp, StatsBaseModel):
    app = models.ForeignKey(Application, null=True, blank=True, limit_choices_to={'review_status__exact': 1, 'published': 1}, verbose_name=_('application'))
    app_list = models.ForeignKey(AppList, verbose_name=_('app list'))
    group = models.ForeignKey(Group, verbose_name=_('user group'),null=True, blank=True, editable=False)
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('title'))
    description = models.TextField(max_length=4096, null=True, blank=True, verbose_name=_('description'))
    icon_url = models.URLField(verify_exists=False, max_length=255, null=True, blank=True, verbose_name=_('icon URL'), \
            help_text=_('Please upload JPEG, PNG, GIF files'))
    icon_path = models.ImageField(storage=LocalFileSystemStorage(), upload_to='static/images/', null=True, blank=True, verbose_name=_('icon path'), \
            help_text=_('Please upload JPEG, PNG, GIF files'))
    extra_infos = models.CharField(max_length=1024, verbose_name=_('extra info'), null=True, blank=True)
    # ALTER TABLE `app_applistitem` ADD COLUMN `extra_infos` varchar(1024) NULL;

    objects = CustomManager()

    def save(self):
        if self.icon_path:
            self.icon_path.name = smart_str(self.icon_path.name)
        super(AppListItem, self).save()

    def attr_readable(self):
        if self.type and self.attr:
            if self.type == RICHITEM_TYPE.APP_DETAILES_PAGE:
                try:
                    app = Application.objects.get(id=long(self.attr))
                    return _('App-%(app_id)s-%(app_name)s') % {'app_id': app.id, 'app_name': app.name}
                except:
                    return _('App with id %(app_id)s does not exists') % {'app_id': self.attr}
            elif self.type == RICHITEM_TYPE.SUBJECT_INFO:
                try:
                    subject = CategorySubject.objects.get(id=long(self.attr))
                    return _('Subject-%(subject_id)s-%(subject_name)s') % {'subject_id': subject.id, 'subject_name': subject.name}
                except:
                    return _('Subject with id %(subject_id)s does not exists') % {'subject_id': self.attr}
        return self.attr
    attr_readable.short_description = _('attr readable')

    class Meta:
        app_label = 'app'
        verbose_name = _('AppListItem')
        verbose_name_plural = _('AppListItem')


class AppReview(models.Model):
    user_id = models.IntegerField(verbose_name=_('user ID'))
    user_name = models.CharField(max_length=255, verbose_name=_('user name'))
    app_version = models.ForeignKey(AppVersion, related_name='reviews', verbose_name=_('application'))
    rate = models.DecimalField(choices=APP_RATES, max_digits=25, decimal_places=1, verbose_name=_('rating'))
    comment = models.TextField(max_length=1023, verbose_name=_('comment'))
    created_time = models.DateTimeField(_('created time'))
    hided = models.BooleanField(default=False, verbose_name=_("hided"))
    published = models.BooleanField(default=True, verbose_name=_("published"))
    sync_status = models.IntegerField(choices=SYNC_STATUS.to_choices(), verbose_name=_("sync status"))
    review_status = models.IntegerField(default=1, choices=REVIEW_STATUS.to_choices(), verbose_name=_('review status'))
    tag = models.IntegerField(default=2, choices=STATS_TAGS.to_choices(), verbose_name=_('tag'))

    def review_id(self):
        return self.id
    review_id.admin_order_field = 'id'
    review_id.short_description = _('review ID')

    def app_version_name(self):
        return self.app_version.app_version()
    app_version_name.short_description = _('application name and version')

    def __unicode__(self):
        return self.comment

    def delete(self):
        self.hided = 1
        self.sync_status = 0
        self.save()

    class Meta:
        app_label = 'app'
        verbose_name = _('Application Review')
        verbose_name_plural = _('Application Reviews')


"""STATISTICS"""
class CategoryStats(Statistics):
    category = models.ForeignKey(Category, related_name='stats', verbose_name=_('category'))
    clicks = models.BigIntegerField(verbose_name=_('clicks'))

    class Meta:
        app_label = 'app'


class ApplicationStats(Statistics):
    app = models.ForeignKey(Application, related_name='stats', verbose_name=_('app'))
    rate = models.DecimalField(default=DECIMAL_0, max_digits=25, decimal_places=5, verbose_name=_('rate'))
    ratings = models.BigIntegerField(default=0, verbose_name=_('ratings'))
    clicks = models.BigIntegerField(default=0, verbose_name=_('clicks'))
    downloads = models.BigIntegerField(default=0, verbose_name=_('downloads'))

    class Meta:
        app_label = 'app'


class AppVersionStats(Statistics):
    appversion = models.ForeignKey(AppVersion, related_name='stats', verbose_name=_('appversion'))
    rate = models.DecimalField(default=DECIMAL_0, max_digits=25, decimal_places=5, verbose_name=_('rate'))
    ratings = models.BigIntegerField(default=0, verbose_name=_('ratings'))
    clicks = models.BigIntegerField(default=0, verbose_name=_('clicks'))
    downloads = models.BigIntegerField(default=0, verbose_name=_('downloads'))

    class Meta:
        app_label = 'app'


class CategoryFoucsImageStats(Statistics):
    categoryfoucsimage = models.ForeignKey(CategoryFoucsImage, related_name='stats', verbose_name=_('categoryfoucsimage'))
    clicks = models.BigIntegerField(default=0, verbose_name=_('clicks'))

    class Meta:
        app_label = 'app'


class CategorySubjectStats(Statistics):
    categorysubject = models.ForeignKey(CategorySubject, related_name='stats', verbose_name=_('categorysubject'))
    clicks = models.BigIntegerField(default=0, verbose_name=_('clicks'))

    class Meta:
        app_label = 'app'


class CategoryRecommendAppStats(Statistics):
    categoryrecommend = models.ForeignKey(CategoryRecommendApp, related_name='stats', verbose_name=_('categoryrecommend'))
    clicks = models.BigIntegerField(default=0, verbose_name=_('clicks'))
    downloads = models.BigIntegerField(default=0, verbose_name=_('downloads'))

    class Meta:
        app_label = 'app'


class PreparedAppStats(Statistics):
    preparedapp = models.ForeignKey(PreparedApp, related_name='stats', verbose_name=_('preparedapp'))
    clicks = models.BigIntegerField(default=0, verbose_name=_('clicks'))
    downloads = models.BigIntegerField(default=0, verbose_name=_('downloads'))

    class Meta:
        app_label = 'app'


class BootAppStats(Statistics):
    bootapp = models.ForeignKey(BootApp, related_name='stats', verbose_name=_('bootapp'))
    clicks = models.BigIntegerField(default=0, verbose_name=_('clicks'))
    downloads = models.BigIntegerField(default=0, verbose_name=_('downloads'))

    class Meta:
        app_label = 'app'


class TopAppStats(Statistics):
    topapp = models.ForeignKey(TopApp, related_name='stats', verbose_name=_('topapp'))
    clicks = models.BigIntegerField(default=0, verbose_name=_('clicks'))
    downloads = models.BigIntegerField(default=0, verbose_name=_('downloads'))

    class Meta:
        app_label = 'app'


class CheckApp(models.Model):
    content_type = models.ForeignKey(ContentType, verbose_name=_('app model'))
    obj_id = models.IntegerField(verbose_name=_("object pk"))
    app = models.ForeignKey("Application",verbose_name=_('application'))
    hided = models.BooleanField(default=False, verbose_name=_("hided"))
    model_name = models.CharField(max_length=128, verbose_name=_('model name'))
    created_time = models.DateTimeField(verbose_name=_("created_time"))

    class Meta:
        app_label = 'app'
        verbose_name = _('Check app status')


class AppMaskOff(Ordered):
    package_name = models.CharField(max_length=255, verbose_name=_('mask off package name'))
    reason = models.TextField(max_length=512, verbose_name=_('mask off reason'))

    class Meta:
        app_label = 'app'
        verbose_name = _('App Mask Off')


#used for tianyi channel package
class AppChannelList(Application):
    objects = CustomManager({'t_status': 6})

    class Meta:
        proxy = True
        app_label = string_with_title("app", _("App list"))
        verbose_name = _('App Channel')
        verbose_name_plural = verbose_name
