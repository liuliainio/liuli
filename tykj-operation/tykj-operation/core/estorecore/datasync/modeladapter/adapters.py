#! -*- coding:utf-8 -*-
import urllib
import logging
from django.db.models import Q
from django.utils import simplejson
from estorecore.db import datetime2timestamp, timestamp2datetime
from estorecore.models.app import Application, AppVersion
from estorecore.models.constants import PUSH_MESSAGE_ACTIONS, GROUP_MAPPING
from estorecore.utils import friendly_size, parse_url, safe_cast

logger = logging.getLogger('estoreoperation')


def _get_app_developer(current_version):
    if current_version.developer:
        return current_version.developer
    versions = AppVersion.objects.filter(app=current_version.app).exclude(developer__exact='').order_by('-version_code')
    if versions:
        return versions[0].developer
    return ''


def _get_prev_version_download_url(app, current_version_id):
    versions = app.versions.all().exclude(pk__exact=current_version_id).\
            filter(~Q(download_url='') | ~Q(download_path='')).order_by('-version_code')
    if versions:
        return versions[0].download_url or parse_url(versions[0].download_path.url)
    return ''


def _get_reviewed_version(app):
    reviewed_versions = AppVersion.objects.filter(app=app, reviewed_desc_preview=1).order_by('-version_code')
    if len(reviewed_versions) > 0:
        return reviewed_versions[0]
    else:
        return app.current_version


def _convert_app_labels(label):
    label_infos = {
            'safe_type': u'未知',    # default value
            'safe_verifiers': [],
            'ad_type': u'未知',    # default value
            'ad_tags': [],
            'privacy_type': u'未知',    # default value
            'privacy_tags': [],
            'other_tags': [],
        }
    if not label:
        return label_infos

    app_labels = simplejson.loads(label)
    safe_tags, ad_tags, other_tags = app_labels['safe']['tag'], app_labels['ad']['tag'], app_labels['others']['tag']
    if safe_tags:
        label_infos['safe_type'] = safe_tags[0]
        if safe_tags[0] == u'安全':
            label_infos['safe_verifiers'] = app_labels['safe']['sub_tag'][u'安全']
    if ad_tags:
        label_infos['ad_type'] = ad_tags[0]
        if ad_tags[0] == u'有广告':
            label_infos['ad_tags'] = app_labels['ad']['sub_tag'][u'有广告']
    if other_tags:
        if u'隐私' in other_tags:
            label_infos['privacy_type'] = u'有隐私'
            label_infos['privacy_tags'] = app_labels['others']['sub_tag'][u'隐私']
            if u'无隐私' in label_infos['privacy_tags']:
                label_infos['privacy_type'] = u'无隐私'
                label_infos['privacy_tags'] = []
            other_tags.remove(u'隐私')
        label_infos['other_tags'] = other_tags

    return label_infos


class ModelAdapter(object):

    def __init__(self, conn_ops):
        self.conn_ops = conn_ops

    def convert_to(self, from_model):
        pass

    def convert_from(self, to_model, data):
        pass


class CategoryAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        if from_model.review_status:
            result_dict.append({
                    'id': from_model.id,
                    'name': from_model.name,
                    'order': from_model.order,
                    'description': from_model.description,
                    'parent_category_id': from_model.parent_category.id if from_model.parent_category else 0,
                    'has_child': from_model.children.count() > 0,
                    'icon_url': from_model.icon_url or parse_url(from_model.icon_path.url if from_model.icon_path else ''),
                    'app_count': from_model.app_counts(),
                })
        return result_dict


def get_latest_appversion(app):
    versions = AppVersion.objects.filter(app=app,published=True,review_status=1).order_by('-version_code')
    if versions:
        latest_version = versions[0]
        return latest_version
    return None


def get_promote_app(app):
    #default not open tianyi promote
    latest_version_dict = {'t_promote': 0}
    #status in blacklist
    if app.t_status == 6:
        latest_version = get_latest_appversion(app)
        current_version = app.current_version
        if not latest_version or not current_version:
            return latest_version_dict
        latest_version_dict.update({
                              't_version_code': current_version.version_code,
                              't_version': current_version.version,
                              't_download_url': current_version.download_url or \
                                                parse_url(current_version.download_path.url if current_version.download_path else ''),
                              't_package_hash': current_version.package_hash,
                              't_promote': 1,
                              'version_code': latest_version.version_code,
                              'package_hash': latest_version.package_hash,
                              'version': latest_version.version,
                              'download_url': latest_version.download_url or \
                                            parse_url(latest_version.download_path.url if latest_version.download_path else ''),
                              })
        if latest_version.version_code > current_version.version_code:
            latest_version_dict.update({'version': 'unknow'})
    return latest_version_dict


class ApplicationAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        current_version = from_model.current_version
        reviewed_version = _get_reviewed_version(from_model)

        blocked_devices = from_model.blocked_devices if from_model.blocked_devices else ''
        unique_devices = set(dev.strip() for dev in blocked_devices.strip().split(',') if dev)

        external_download_url = current_version.external_download_url if current_version.external_download_url else ''
        external_download_url_set =  set(link for link in external_download_url.strip().split(' ') if link)

        if current_version and from_model.review_status:
            result = {
                    'id': from_model.id,
                    'tid': from_model.t_id if (from_model.t_id and from_model.t_status == 1) else 0,
                    'download_tid': from_model.t_id if (from_model.t_id and from_model.t_status == 1 and (from_model.t_chargemode not in (0, 4) or not (current_version.download_url or \
                            parse_url(current_version.download_path.url if current_version.download_path else '')))) else 0,
                    'backup_tid': from_model.t_id if from_model.t_id else 0,
                    'charge_mode': from_model.t_chargemode,
                    'name': from_model.name,
                    'developer': _get_app_developer(current_version),
                    'description': reviewed_version.description,
                    'update_note': current_version.update_note or "",
                    'price': float(current_version.price),
                    'rate': float(from_model.rate),
                    'package_name': from_model.package_name,
                    'package_sig': from_model.package_sig,
                    'package_hash': current_version.package_hash,
                    'download_count': from_model.downloads_count,
                    'preview_icon_urls': reviewed_version.icon_urls(),
                    'icon_url': current_version.icon_url or parse_url(current_version.icon_path.url if current_version.icon_path else ''),
                    'download_url': current_version.download_url or \
                            parse_url(current_version.download_path.url if current_version.download_path else ''),
                    'external_download_urls':list(external_download_url_set),
                    'version': current_version.version,
                    'version_code': current_version.version_code,
                    'size': friendly_size(current_version.size),
                    'category_id': from_model.category.id,
                    'sub_category_id': from_model.sub_category.id,
                    'cate_name': from_model.category.name,
                    'sub_cate_name': from_model.sub_category.name,
                    'update_date': datetime2timestamp(current_version.modified_time, convert_to_utc=True),
                    'rate_count': from_model.reviews_count,
                    'order': from_model.order,
                    'min_sdk_version': current_version.min_sdk_version,
                    'promote': -1,
                    'blocked_devices': list(unique_devices),
                }
            result.update(_convert_app_labels(from_model.label))

            #tianyi blacklist app control
            #promote_result = get_promote_app(from_model)
            #result.update(promote_result)
            if not result['download_url']:
                result['download_url'] = _get_prev_version_download_url(from_model, current_version.id)
            result_dict.append(result)
        return result_dict


class AppListAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        result_dict.append({
                'id': from_model.id,
                'name': from_model.name,
                'codename': from_model.codename,
            })
        return result_dict



def get_region_group(from_model):
    group_content = ''
    if from_model.group:
        name = from_model.group.name
        if name in GROUP_MAPPING:
            group_content = GROUP_MAPPING[name]
    return group_content


class PhoneRegionAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        model = {
            'pk': from_model.id,
            'phone': from_model.phone,
            'province': from_model.province_pinyin,
        }

        result_dict.append(model)
        return result_dict


class AppListItemAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        group_content = get_region_group(from_model)
        model = {
                'pk': from_model.id,
                'app_list_id': from_model.app_list.id,
                'order': from_model.order,
                'title': from_model.title,
                'description': from_model.description,
                'icon_url': from_model.icon_url or parse_url(from_model.icon_path.url if from_model.icon_path else ''),
                'large_icon_url': from_model.icon_url or parse_url(from_model.icon_path.url if from_model.icon_path else ''),
                'image_url': from_model.icon_url or parse_url(from_model.icon_path.url if from_model.icon_path else ''),
                'attr': from_model.attr,
                'type': from_model.type,
                'extra_infos': {} if not from_model.extra_infos else simplejson.loads(from_model.extra_infos),
                'region': group_content,
            }
        if from_model.app and from_model.app.current_version and from_model.app.review_status:
            current_version = from_model.app.current_version
            reviewed_version = _get_reviewed_version(from_model.app)
            app_infos = {
                    'id': from_model.app.id,
                    'tid': from_model.app.t_id if (from_model.app.t_id and from_model.app.t_status == 1) else 0,
                    'download_tid': from_model.app.t_id if (from_model.app.t_id and from_model.app.t_status == 1 and (current_version.t_status == 6 or from_model.app.t_chargemode not in (0, 4) or not (current_version.download_url or \
                            parse_url(current_version.download_path.url if current_version.download_path else '')))) else 0,
                    'backup_tid': from_model.app.t_id if from_model.app.t_id else 0,
                    'name': from_model.app.name,
                    'developer': _get_app_developer(current_version),
                    'description': reviewed_version.description,
                    'preview_icon_urls': reviewed_version.icon_urls(),
                    'package_name': from_model.app.package_name,
                    'package_sig': from_model.app.package_sig,
                    'version': current_version.version,
                    'version_code': str(current_version.version_code),
                    'tag': from_model.app.tag,
                    'price': float(current_version.price),
                    'rate': float(from_model.app.rate),
                    'icon_url': current_version.icon_url or \
                            parse_url(current_version.icon_path.url if current_version.icon_path else ''),
                    'category_id': from_model.app.category.id if from_model.app.category else 0,
                    'cate_name': from_model.app.category.name if from_model.app.category else '',
                    'sub_category_id': from_model.app.sub_category.id,
                    'sub_cate_name': from_model.app.sub_category.name,
                    'download_count': from_model.app.downloads_count,
                    'size': friendly_size(current_version.size),
                    'update_time': datetime2timestamp(current_version.modified_time, convert_to_utc=True),
                    'min_sdk_version': current_version.min_sdk_version,
                }
            app_infos.update(_convert_app_labels(from_model.app.label))
            model.update({'app': app_infos})
        result_dict.append(model)
        return result_dict


class RecommendAppAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        group_content = get_region_group(from_model)
        current_version = from_model.app.current_version
        if current_version and from_model.app.review_status:
            app_infos = {
                    'pk': from_model.id,
                    'id': from_model.app.id,
                    'tid': from_model.app.t_id if (from_model.app.t_id and from_model.app.t_status == 1) else 0,
                    'download_tid': from_model.app.t_id if (from_model.app.t_id and from_model.app.t_status == 1 and (current_version.t_status == 6 or from_model.app.t_chargemode not in (0, 4) or not (current_version.download_url or \
                            parse_url(current_version.download_path.url if current_version.download_path else '')))) else 0,
                    'backup_tid': from_model.app.t_id if from_model.app.t_id else 0,
                    'name': from_model.app.name,
                    'tag': from_model.app.tag,
                    'version': current_version.version,
                    'version_code': current_version.version_code,
                    'package_name': from_model.app.package_name,
                    'price': float(current_version.price),
                    'rate': float(from_model.app.rate),
                    'icon_url': current_version.icon_url or \
                            parse_url(current_version.icon_path.url if current_version.icon_path else ''),
                    'cate_name': from_model.app.category.name,
                    'sub_cate_name': from_model.app.sub_category.name,
                    'order': from_model.order,
                    'type': from_model.type,
                    'download_count': from_model.app.downloads_count,
                    'size': friendly_size(current_version.size),
                    'min_sdk_version': current_version.min_sdk_version,
                    'region':group_content,
                }
            app_infos.update(_convert_app_labels(from_model.app.label))
            result_dict.append(app_infos)
        return result_dict


class PreparedAppAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        current_version = from_model.app.current_version
        reviewed_version = _get_reviewed_version(from_model.app)
        if current_version and from_model.app.review_status:
            app_infos = {
                    'pk': from_model.id,
                    'id': from_model.app.id,
                    'tid': from_model.app.t_id if (from_model.app.t_id and from_model.app.t_status == 1) else 0,
                    'download_tid': from_model.app.t_id if (from_model.app.t_id and from_model.app.t_status == 1 and (current_version.t_status == 6 or from_model.app.t_chargemode not in (0, 4) or not (current_version.download_url or \
                            parse_url(current_version.download_path.url if current_version.download_path else '')))) else 0,
                    'backup_tid': from_model.app.t_id if from_model.app.t_id else 0,
                    'name': from_model.app.name,
                    'order': from_model.order,
                    'description': reviewed_version.description,
                    'version': current_version.version,
                    'version_code': current_version.version_code,
                    'package_name': from_model.app.package_name,
                    'price': float(current_version.price),
                    'rate': float(from_model.app.rate),
                    'icon_url': current_version.icon_url or parse_url(current_version.icon_path.url if current_version.icon_path else ''),
                    'cate_name': from_model.app.category.name,
                    'sub_cate_name': from_model.app.sub_category.name,
                    'pub_date': datetime2timestamp(current_version.pub_date, convert_to_utc=True),
                    'download_count': from_model.app.downloads_count,
                    'size': friendly_size(current_version.size),
                    'min_sdk_version': current_version.min_sdk_version,
                }
            app_infos.update(_convert_app_labels(from_model.app.label))
            result_dict.append(app_infos)
        return result_dict


class BootAppAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        current_version = from_model.app.current_version
        reviewed_version = _get_reviewed_version(from_model.app)
        if current_version and from_model.app.review_status:
            app_infos = {
                    'pk': from_model.id,
                    'boot_app_type': from_model.boot_app_type,
                    'id': from_model.app.id,
                    'tid': from_model.app.t_id if (from_model.app.t_id and from_model.app.t_status == 1) else 0,
                    'download_tid': from_model.app.t_id if (from_model.app.t_id and from_model.app.t_status == 1 and (current_version.t_status == 6 or from_model.app.t_chargemode not in (0, 4) or not (current_version.download_url or \
                            parse_url(current_version.download_path.url if current_version.download_path else '')))) else 0,
                    'backup_tid': from_model.app.t_id if from_model.app.t_id else 0,
                    'name': from_model.app.name,
                    'order': from_model.order,
                    'description': reviewed_version.description,
                    'version': current_version.version,
                    'version_code': current_version.version_code,
                    'package_name': from_model.app.package_name,
                    'price': float(current_version.price),
                    'rate': float(from_model.app.rate),
                    'icon_url': current_version.icon_url or parse_url(current_version.icon_path.url if current_version.icon_path else ''),
                    'cate_name': from_model.app.category.name,
                    'sub_cate_name': from_model.app.sub_category.name,
                    'pub_date': datetime2timestamp(current_version.pub_date, convert_to_utc=True),
                    'download_count': from_model.app.downloads_count,
                    'size': friendly_size(current_version.size),
                    'min_sdk_version': current_version.min_sdk_version,
                }
            app_infos.update(_convert_app_labels(from_model.app.label))
            result_dict.append(app_infos)
        return result_dict


class SubjectItemAdapter(ModelAdapter):

    def convert_to(self, from_model):
        subject_item = {
                'id': from_model.id,
                'subject_id': from_model.subject.id,
                'title': from_model.title,
                'description': from_model.description,
                'icon_url': from_model.icon_url or parse_url(from_model.icon_path.url if from_model.icon_path else ''),
                'order': from_model.order,
                'subject_info': {
                        'name': from_model.subject.name,
                        'sub_title': from_model.subject.sub_title,
                        'click_count': from_model.subject.clicks_count,
                        'description': from_model.subject.description,
                        'pub_date': datetime2timestamp(from_model.subject.pub_date, convert_to_utc=True),
                    }
            }
        apps = []
        for subject_app in from_model.apps.all().order_by('order'):
            current_version = subject_app.app.current_version
            reviewed_version = _get_reviewed_version(subject_app.app)
            if current_version:
                app_infos = {
                        'pk': subject_app.id,
                        'order': subject_app.order,
                        'id': subject_app.app.id,
                        'tid': subject_app.app.t_id if (subject_app.app.t_id and subject_app.app.t_status == 1) else 0,
                        'download_tid': subject_app.app.t_id if (subject_app.app.t_id and subject_app.app.t_status == 1 and (current_version.t_status == 6 or subject_app.app.t_chargemode not in (0, 4) or not (current_version.download_url or \
                                parse_url(current_version.download_path.url if current_version.download_path else '')))) else 0,
                        'backup_tid': subject_app.app.t_id if subject_app.app.t_id else 0,
                        'name': subject_app.app.name,
                        'description': reviewed_version.description,
                        'version': current_version.version,
                        'version_code': current_version.version_code,
                        'package_name': subject_app.app.package_name,
                        'price': float(subject_app.app.price),
                        'rate': float(subject_app.app.rate),
                        'icon_url': current_version.icon_url or parse_url(current_version.icon_path.url if current_version.icon_path else ''),
                        'pub_date': datetime2timestamp(current_version.pub_date, convert_to_utc=True),
                        'download_count': subject_app.app.downloads_count,
                        'size': friendly_size(current_version.size),
                        'min_sdk_version': current_version.min_sdk_version,
                    }
                app_infos.update(_convert_app_labels(subject_app.app.label))
                apps.append(app_infos)
        subject_item['apps'] = apps
        return [subject_item]


class KuWanItemAdapter(ModelAdapter):

    def convert_to(self, from_model):
        kuwan_item = {
                'id': from_model.id,
                't_id': from_model.t_id,
                'list_type': from_model.list_type,
                'title': from_model.title,
                'description': from_model.description,
                'price': float(from_model.price),
                'icon_url': from_model.icon_url or parse_url(from_model.icon_path.url if from_model.icon_path else ''),
                'order': from_model.order,
            }
        apps = []
        for kuwan_app in from_model.apps.all().order_by('order'):
            current_version = kuwan_app.app.current_version
            reviewed_version = _get_reviewed_version(from_model.app)
            app_infos = {
                    'pk': kuwan_app.id,
                    'order': kuwan_app.order,
                    'id': kuwan_app.app.id,
                    'tid': kuwan_app.app.t_id if (kuwan_app.app.t_id and kuwan_app.app.t_status == 1) else 0,
                    'download_tid': kuwan_app.app.t_id if (kuwan_app.app.t_id and kuwan_app.app.t_status == 1 and (current_version.t_status == 6 or kuwan_app.app.t_chargemode not in (0, 4) or not (current_version.download_url or \
                            parse_url(current_version.download_path.url if current_version.download_path else '')))) else 0,
                    'backup_tid': kuwan_app.app.t_id if kuwan_app.app.t_id else 0,
                    'name': kuwan_app.app.name,
                    'description': reviewed_version.description,
                    'version': current_version.version,
                    'version_code': current_version.version_code,
                    'package_name': kuwan_app.app.package_name,
                    'price': float(kuwan_app.app.price),
                    'rate': float(kuwan_app.app.rate),
                    'icon_url': current_version.icon_url or parse_url(current_version.icon_path.url if current_version.icon_path else ''),
                    'pub_date': datetime2timestamp(current_version.pub_date, convert_to_utc=True),
                    'download_count': kuwan_app.app.downloads_count,
                    'size': friendly_size(current_version.size),
                    'min_sdk_version': current_version.min_sdk_version,
                }
            app_infos.update(_convert_app_labels(kuwan_app.app.label))
            apps.append(app_infos)
        kuwan_item['apps'] = apps
        return [kuwan_item]


class FoucsImageAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        group_content = get_region_group(from_model)
        if from_model.review_status:
            result_dict.append({
                'id': from_model.id,
                'type': from_model.type,
                'attr': from_model.attr,
                'area': from_model.area,
                'order': from_model.order,
                'pub_date': datetime2timestamp(from_model.pub_date, convert_to_utc=True),
                'icon_url': from_model.icon_url or parse_url(from_model.icon_path.url if from_model.icon_path else ''),
                'category_id': from_model.category.id if from_model.category else 0,
                'recommend_type': from_model.recommend_type,
                'region': group_content,
                'cooperate_list_id': from_model.cooperate_list_id.strip() if from_model.cooperate_list_id else '',
                'cooperate_list_name': from_model.cooperate_list_name.strip() if from_model.cooperate_list_name else ''
            })
        return result_dict


class SubjectAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        if from_model.review_status:
            result_dict.append({
                    'id': from_model.id,
                    'name': from_model.name,
                    'sub_title': from_model.sub_title,
                    'click_count': from_model.clicks_count,
                    'order': from_model.order,
                    'description': from_model.description,
                    'pub_date': datetime2timestamp(from_model.pub_date, convert_to_utc=True),
                    'icon_url': from_model.icon_url or parse_url(from_model.icon_path.url if from_model.icon_path else ''),
                    'large_icon_url': from_model.large_icon_url or parse_url(from_model.large_icon_path.url if from_model.large_icon_path else ''),
                    'subject_tml': from_model.subject_tml,
                })
        return result_dict


class TopAppAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        current_version = from_model.app.current_version
        reviewed_version = _get_reviewed_version(from_model.app)
        if current_version and from_model.app.review_status:
            app_infos = {
                    'pk': from_model.id,
                    'id': from_model.app.id,
                    'tid': from_model.app.t_id if (from_model.app.t_id and from_model.app.t_status == 1) else 0,
                    'download_tid': from_model.app.t_id if (from_model.app.t_id and from_model.app.t_status == 1 and (current_version.t_status == 6 or from_model.app.t_chargemode not in (0, 4) or not (current_version.download_url or \
                            parse_url(current_version.download_path.url if current_version.download_path else '')))) else 0,
                    'backup_tid': from_model.app.t_id if from_model.app.t_id else 0,
                    'name': from_model.app.name,
                    'order': from_model.order,
                    'short_desc': from_model.short_desc,
                    'description': reviewed_version.description,
                    'version': current_version.version,
                    'version_code': current_version.version_code,
                    'package_name': from_model.app.package_name,
                    'price': float(current_version.price),
                    'rate': float(from_model.app.rate),
                    'icon_url': current_version.icon_url or parse_url(current_version.icon_path.url if current_version.icon_path else ''),
                    'category_id': from_model.app.category.id,
                    'sub_category_id': from_model.app.sub_category.id,
                    'cate_name': from_model.app.category.name,
                    'sub_cate_name': from_model.app.sub_category.name,
                    'pub_date': datetime2timestamp(current_version.pub_date, convert_to_utc=True),
                    'download_count': from_model.app.downloads_count,
                    'size': friendly_size(current_version.size),
                    'min_sdk_version': current_version.min_sdk_version,
                }
            app_infos.update(_convert_app_labels(from_model.app.label))
            result_dict.append(app_infos)
        return result_dict


class ActivityAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        group_content = get_region_group(from_model)
        if from_model.review_status:
            result_dict.append({
                    'id': from_model.id,
                    'title': from_model.title,
                    'start_date': datetime2timestamp(from_model.start_date, convert_to_utc=True),
                    'end_date': datetime2timestamp(from_model.end_date, convert_to_utc=True),
                    'description': from_model.description,
                    'icon_url': from_model.icon_url or parse_url(from_model.icon_path.url if from_model.icon_path else ''),
                    'large_icon_url': from_model.large_icon_url or parse_url(from_model.large_icon_path.url if from_model.large_icon_path else ''),
                    'status': from_model.status,
                    'type': from_model.type,
                    'attr': from_model.attr,
                    'tag': from_model.tag,
                    'order': from_model.order,
                    'region': group_content,
                })
        return result_dict


class AppReviewAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        if from_model.app_version:
            result_dict.append({
                    'id': from_model.id,
                    'user_id': from_model.user_id,
                    'user_name': from_model.user_name,
                    'app_id': from_model.app_version.app.id,
                    'app_version': from_model.app_version.version,
                    'rate': float(from_model.rate),
                    'comment': from_model.comment,
                    'created_time': datetime2timestamp(from_model.created_time, convert_to_utc=True),
                })
        return result_dict

    def convert_from(self, to_model, data):
        to_model.user_id = int(data.get('user_id', 0))
        to_model.user_name = data.get('user_name', '')
        to_model.rate = data.get('rate', 0)
        to_model.comment = data.get('comment', '')
        to_model.created_time = timestamp2datetime(data.get('created_time', 0), convert_to_local=True)
        to_model.sync_status = 1
        to_model.review_status = 1
        to_model.tag = 1
        apps = Application.objects.filter(pk=int(data.get('app_id', 0)))
        to_model.app_version = apps[0].current_version if apps else None
        return to_model


class LoginPictureAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        group_content = get_region_group(from_model)
        if from_model.review_status:
            result_dict.append({
                    'id': from_model.id,
                    'name': from_model.name,
                    'search_keyword': from_model.search_keyword if from_model.search_keyword else '',
                    'path': from_model.url or parse_url(from_model.path.url if from_model.path else ''),
                    'start_date': datetime2timestamp(from_model.start_date, convert_to_utc=True),
                    'end_date': datetime2timestamp(from_model.end_date, convert_to_utc=True),
                    'is_default': from_model.is_default,
                    'type':from_model.type,
                    'attr':from_model.attr,
                    'region': group_content,
                    'home_banner': from_model.home_banner.strip() if from_model.home_banner else '',
                })
        return result_dict


class SearchKeywordAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        result_dict.append({
                'id': from_model.id,
                'order': from_model.order,
                'keyword': from_model.keyword,
                'search_count': from_model.search_count,
                'search_trend': from_model.search_trend,
            })
        return result_dict

class KeywordLocationAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        result_dict.append({
                'id': from_model.id,
                'keyword': from_model.keyword,
                'location': from_model.location,
                'app_id': from_model.app.id,
            })
        return result_dict

class UpdateAppAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        if from_model.review_status:
            result_dict.append({
                    'id': from_model.id,
                    'package_name': from_model.package_name,
                    'version_name': from_model.version_name,
                    'source': from_model.source,
                    'version_code': from_model.version_code,
                    'os': from_model.os,
                    'os_version': from_model.os_version,
                    'resolution': from_model.resolution,
                    'cpu': from_model.cpu,
                    'model': from_model.model,
                    'rom': from_model.rom,
                    'update_time': datetime2timestamp(from_model.created_time, convert_to_utc=True),
                    'download_url': from_model.download_url or parse_url(from_model.download_path.url if from_model.download_path else ''),
                    'package_hash': from_model.package_hash or "",
                    'button': from_model.get_buttons(),
                    'title': from_model.title,
                    'content_title': from_model.content_title,
                    'change_log': from_model.change_log,
                    'is_auto': from_model.is_auto,
                    'is_force': from_model.is_force,
                    'is_patch': from_model.is_patch,
                    'package_size': from_model.package_size,
                    'channel_promote': from_model.channel_promote,
                    'device': from_model.device,
                })
        return result_dict


class FeedbackAdapter(ModelAdapter):

    def convert_from(self, to_model, data):
        to_model.source = data.get('source', '')
        to_model.user_id = int(data.get('user_id', 0))
        new_content = data.get('content', '{}')
        to_model.content = new_content if new_content else '{}'
        if to_model.source == 'uninstall':
            try:
                content = simplejson.loads(to_model.content)
                if content.get('feedback_str', ''):
                    to_model.content = content['feedback_str']
            except Exception, e:
                logger.exception('error: %s,%s' % (data.get('uni_token','None'),e))
        to_model.extras = data.get('extras', '')
        to_model.created_time = timestamp2datetime(data.get('created_time', 0), convert_to_local=True)
        return to_model
'''
    def convert_from(self, to_model, data):
        to_model.user_id = int(data.get('user_id', 0))
        to_model.content = data.get('content', '')
        to_model.created_time = timestamp2datetime(data.get('created_time', 0), convert_to_local=True)
        return to_model
'''


def _get_message_action_url(message):
    url_format = 'estore://%(action)s/%(value)s'
    message_info = {'action': message.action, 'value': message.value}

    if message.action in (PUSH_MESSAGE_ACTIONS.APP_DETAILES_PAGE, PUSH_MESSAGE_ACTIONS.SHORT_CUT_DETAIL_PAGE):
        try:
            app = Application.objects.get(pk__exact=int(message.value))
        except:
            app = None
            logger.exception('Get app info failed, app_id: %s' % message.value)

        current_version = app.current_version
        app_infos = {
                'packagename': app.package_name if app else '',
                'name': app.name.encode('utf-8') if app else '',
                'app_id': app.id if app else '',
                'tid': app.t_id if (app.t_id and app.t_status == 1) else 0,
                'download_tid': app.t_id if (app.t_id and app.t_status == 1 and (current_version.t_status == 6 or app.t_chargemode not in (0, 4) or not (current_version.download_url or \
                        parse_url(current_version.download_path.url if current_version.download_path else '')))) else 0,
                'backup_tid': app.t_id if app.t_id else 0,
                'marketid': 'estore-cnet',
            }
        message_info['value'] = '?%s' % urllib.urlencode(app_infos)
        message_info['action'] = PUSH_MESSAGE_ACTIONS.APP_DETAILES_PAGE
        return {
                'url': url_format % message_info,
                'app_id': app.id if app else '',
                'package_name': app.package_name if app else '',
                'name': app.name if app else '',
                'version_name': app.current_version.version if app and app.current_version else '',
                'icon_url': app.current_version.icon_url or parse_url(app.current_version.icon_path.url) \
                        if app and app.current_version else '',
            }
    elif message.action in (PUSH_MESSAGE_ACTIONS.URL, PUSH_MESSAGE_ACTIONS.SHORT_CUT_URL):
        return {'url': message.value}
    elif message.action == PUSH_MESSAGE_ACTIONS.SUBJECT_INFO:
        return {'url': url_format % message_info}


def _get_click_value(from_model):
    try:
        if safe_cast(from_model.value, int) is None:
            app = Application.objects.get(package_name__exact=from_model.value)
        else:
            app = Application.objects.get(pk__exact=int(from_model.value))
    except:
        app = None

    current_version = app.current_version
    click_values = {
                'tid': app.t_id if (app.t_id and app.t_status == 1) else 0,
                'download_tid': app.t_id if (app.t_id and app.t_status == 1 and (current_version.t_status == 6 or app.t_chargemode not in (0, 4) or not (current_version.download_url or \
                        parse_url(current_version.download_path.url if current_version.download_path else '')))) else 0,
                'backup_tid': app.t_id if app.t_id else 0,
                'app_id': app.id if app else '',
                'app': app.package_name if app else '',
                'package_name': app.package_name if app else '',
                'name': app.name if app else '',
                'icon_url': app.current_version.icon_url or parse_url(app.current_version.icon_path.url) \
                        if app and app.current_version else '',
            }
    return click_values

_CLICK_ACTION_MAPPING = {
        PUSH_MESSAGE_ACTIONS.DOWNLOAD_APP: 'LaunchOrDownload',
        PUSH_MESSAGE_ACTIONS.SHORT_CUT_DOWNLOAD_APP: 'LaunchOrDownload',
        PUSH_MESSAGE_ACTIONS.DOWNLOADB: 'LaunchOrDownload',
        PUSH_MESSAGE_ACTIONS.LAUNCHB: 'Launch',
    }
_ACTIONS = {
        PUSH_MESSAGE_ACTIONS.SHORT_CUT_URL: 'CreateShortcut',
        PUSH_MESSAGE_ACTIONS.SHORT_CUT_DETAIL_PAGE: 'CreateShortcut',
        PUSH_MESSAGE_ACTIONS.SHORT_CUT_DOWNLOAD_APP: 'CreateShortcut',
        PUSH_MESSAGE_ACTIONS.DOWNLOADB: 'DownloadB',
        PUSH_MESSAGE_ACTIONS.LAUNCHB: 'LaunchB',
    }


class PushMessageAdapter(ModelAdapter):

    def convert_to(self, from_model):
        message_infos = {
                'id': from_model.id,
                'message_id': from_model.id + 10000,
                'action': _ACTIONS[from_model.action] if from_model.action in _ACTIONS else 'Notification',
                'value': {
                        'display_area': from_model.display_area,
                        'click_value': _get_click_value(from_model) if from_model.action in _CLICK_ACTION_MAPPING \
                                else _get_message_action_url(from_model),
                        'click_action': 'OpenURL' if from_model.action not in _CLICK_ACTION_MAPPING \
                                else _CLICK_ACTION_MAPPING[from_model.action],
                        'description': from_model.content,
                        'clearable': True,
                        'title': from_model.title,
                        'icon_url': '' if not from_model.icon_url and not from_model.icon_path else \
                                (from_model.icon_url or parse_url(from_model.icon_path.url)),
                    },
                'status': from_model.status,
                'created_time': datetime2timestamp(from_model.created_time, convert_to_utc=True),
                'last_modified': datetime2timestamp(from_model.modified_time, convert_to_utc=True),
                'not_valid_before': datetime2timestamp(from_model.invalid_before, convert_to_utc=True),
                'not_valid_after': datetime2timestamp(from_model.invalid_after, convert_to_utc=True),
                'client_id': from_model.client_id,
                'category': from_model.category or 'N/A',
                'short_message': from_model.short_message or 'N/A',
            }
        if from_model.action == PUSH_MESSAGE_ACTIONS.LAUNCHB:
            message_infos['value'].update(message_infos['value']['click_value'])
            del message_infos['value']['click_value']
        if from_model.extra_infos:
            message_infos['value'].update(simplejson.loads(from_model.extra_infos))
        if from_model.targets:
            message_infos['targets'] = simplejson.loads(from_model.targets)
        return [message_infos]


class AppMaskOffAdapter(ModelAdapter):

    def convert_to(self, from_model):
        result_dict = []
        result_dict.append({
                'id': from_model.id,
                'package_name': from_model.package_name,
            })
        return result_dict


class LocalEntryAdapter(ModelAdapter):
    support_operator = ['>', '<', '=', '>=', '<=']
    def _parse_condition(self, condition):
        import re
        condition = condition.strip()
        if condition and len(condition) > 1:
            result = re.split(r'\s+', condition)
            if len(result) == 2:
                operator, values = result
                if operator in self.support_operator and values.isdigit():
                    return '%s %s' % ('%s', condition)
            return 'False'
        else:
            return 'True'


    def convert_to(self, from_model):
        result_dict = []
        result_dict.append({
                'id': from_model.id,
                'name': from_model.name,
                'action': from_model.action,
                'value': from_model.value.strip(),
                'icon_url': from_model.icon_path.url,
                'parameter': from_model.parameter,
                'order': from_model.order,
                'condition': self._parse_condition(from_model.condition),
            })
        return result_dict
