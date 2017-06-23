import logging
import datetime
from django.conf import settings

from estorecore.datasync.modeladapter import get_adapter

logger = logging.getLogger('estorecore')


def sync_to_production(modeladmin, request=None):
    adapter = get_adapter(modeladmin.model)
    db_conn = adapter.conn_ops['db'](settings.MONGODB_CONF)
    update_table = adapter.conn_ops['table']
    time_start = int(datetime.datetime.now().strftime('%S'))
    time_end = (time_start + 45) % 60

    if request:
        need_sync_items = modeladmin.queryset(request).filter(sync_status=0, review_status__in=[1, 2])
    else:
        need_sync_items = modeladmin.model.objects.filter(sync_status=0, review_status__in=[1, 2])
    sync_successed = 0
    sync_failed = 0
    if request.GET.get('first', ''):
        return {'all': len(need_sync_items)}
    for i, obj in enumerate(need_sync_items):
        can_upsert = obj.published and not obj.hided
        to_objs = []
        try:
            to_objs = adapter.convert_to(obj)
            if not to_objs:
                msg = 'convert to failed %s, id: %s' % (modeladmin.model, obj.pk)
                logger.warn(msg)
                sync_failed += 1
            else:
                for to_obj in to_objs:
                    cond = {'pk': to_obj['pk']} if 'pk' in to_obj else {'id': to_obj['id']}
                    if can_upsert:
                        db_conn.upsert_item(update_table, cond, to_obj, upsert=True)
                    else:
                        db_conn.delete_item(update_table, cond)
                obj.sync_status = 1
                obj.save()
                sync_successed += 1
        except Exception:
            msg = 'sync failed %s, id: %s' % (modeladmin.model, obj.pk)
            logger.exception(msg)
            sync_failed += 1
        time_end2 = int(datetime.datetime.now().strftime('%S'))
        if time_end2 == time_end:
            break
    return {'suc': sync_successed, 'err': sync_failed, 'all': len(need_sync_items)}


class RemoteServer(object):
    pass
