import sys
import traceback
from django.conf import settings

from estorecore.datasync.modeladapter import get_adapter
from estorecore.models.app import Application, CategoryRecommendApp, \
        TopApp, SubjectItem, PreparedApp, CategoryFoucsImage, BootApp, AppListItem


def sync_single_app(app):
    sync_obj(app, Application)
    _sync_from_list(app)


def sync_obj(obj, cls):
    adapter = get_adapter(cls)
    db_conn = adapter.conn_ops['db'](settings.MONGODB_CONF)
    update_table = adapter.conn_ops['table']
    to_objs = adapter.convert_to(obj)
    for to_obj in to_objs:
        cond = {'pk': to_obj['pk']} if 'pk' in to_obj else {'id': to_obj['id']}
        if obj.published:
            try:
                db_conn.upsert_item(update_table, cond, to_obj, upsert=True)
            except:
                trace_stack = '\n'.join(traceback.format_exception(*sys.exc_info()))
                print 'cond: %s, obj:%s, e: %s' % (cond, to_obj, trace_stack)
        else:
            try:
                db_conn.delete_item(update_table, cond)
            except:
                trace_stack = '\n'.join(traceback.format_exception(*sys.exc_info()))
                print 'cond: %s, e: %s' % (cond, trace_stack)
    obj.sync_status = 1
    obj.save()


def _sync_from_list(app):
    for items, cls in (
            (app.preparedapp_set.all(), PreparedApp),
            (app.bootapp_set.all(), BootApp),
            (app.topapp_set.all(), TopApp),
            (app.applistitem_set.all(), AppListItem),
            (app.item.all(), SubjectItem),
            (app.categoryrecommendapp_set.all(), CategoryRecommendApp),
            (CategoryFoucsImage.objects.filter(type=3, attr=app.id).all(), CategoryFoucsImage)
            ):
        for item in items:
            try:
                if cls == SubjectItem:
                    item = item.subject_item
                item.sync_status = 0
                if not app.published:
                    item.review_status = 2
                item.published = (app.published or app.hided)
                item.save()
                sync_obj(item, cls)
            except Exception, e:
                pass
