#! -*- coding: utf-8 -*-
from estoreoperation.admin.applist.models import NewestRecommendApp, MatchestRecommendApp,\
        HomeNewRecommendApp, HottestRecommendApp, ApplicationTopApp, GameTopApp, ReadingTopApp, MusicVideoTopApp
from estorecore.models.app import AppListItem, AppList
from reporting.db import get_reporting_store
from django.conf import settings
import logging


logger = logging.getLogger("django")

DB_CONF = {
    'reporting': {
        'conn_str': settings.REPORTING_DB_CONF
    }}

store = get_reporting_store(DB_CONF)

OUTER_RECOMMENED = 'featured_download'
OUTER_LATEST = 'featured_latest'
OUTER_NECESSARY = 'featured_hotapps_download'
OUTER_HOTTEST = 'none'
OUTER_HOMENEW = 'none'

#type:mysql_source
sources_search_map = {
    'search_click': ['search_search'],
    'search_keyword_click': ['search_keyword_search'],
    'detail_app_download': ['detail_app_search'],
    'detail_game_download': ['detail_game_search'],
    'detail_media_download': ['detail_media_search'],
    'detail_reading_download': ['detail_reading_search'],
    'search_download': ['search'],
}


#type:mysql_source
sources_detail_map = {
    'recommend': {
        'app': {'detail': 'detail_app_featured_recommended','outer': OUTER_RECOMMENED},
        'game': {'detail': 'detail_game_featured_recommended','outer': OUTER_RECOMMENED},
        'media': {'detail': 'detail_media_featured_recommended','outer': OUTER_RECOMMENED},
        'reading': {'detail': 'detail_reading_featured_recommended','outer': OUTER_RECOMMENED},
    },
    'latest': {
        'app': {'detail': 'detail_app_featured_latest','outer': OUTER_LATEST},
        'game': {'detail': 'detail_game_featured_latest','outer': OUTER_LATEST},
        'media': {'detail': 'detail_media_featured_latest','outer': OUTER_LATEST},
        'reading': {'detail': 'detail_reading_featured_latest','outer': OUTER_LATEST},
    },
    'rank': {
        'app': {'detail': 'detail_app_rank_app','outer': 'rank_app'},
        'game': {'detail': 'detail_game_rank_game','outer': 'rank_game'},
        'media': {'detail': 'detail_media_rank_media','outer': 'rank_media'},
        'reading': {'detail': 'detail_reading_rank_reading','outer': 'rank_reading'},
    },
    'necessary': {
        'app': {'detail': 'detail_app_featured_hotapps','outer': OUTER_NECESSARY},
        'game': {'detail': 'detail_game_featured_hotapps','outer': OUTER_NECESSARY},
        'media': {'detail': 'detail_media_featured_hotapps','outer': OUTER_NECESSARY},
        'reading': {'detail': 'detail_reading_featured_hotapps','outer': OUTER_NECESSARY},
    },
    'hottest': {
        'app': {'detail': 'detail_app_featured_hottest','outer': OUTER_HOTTEST},
        'game': {'detail': 'detail_game_featured_hottest','outer': OUTER_HOTTEST},
        'media': {'detail': 'detail_media_featured_hottest','outer': OUTER_HOTTEST},
        'reading': {'detail': 'detail_reading_featured_hottest','outer': OUTER_HOTTEST},
    },
    'homenew': {
        'app': {'detail': 'detail_app_featured_first','outer': OUTER_HOMENEW},
        'game': {'detail': 'detail_game_featured_first','outer': OUTER_HOMENEW},
        'media': {'detail': 'detail_media_featured_first','outer': OUTER_HOMENEW},
        'reading': {'detail': 'detail_reading_featured_first','outer': OUTER_HOMENEW},
    },
}

necessary_list = AppList.objects.get(codename='bangdanbibei')
necessary_listitem = necessary_list.applistitem_set

listitem_objects_map = {
    ('latest','*'): NewestRecommendApp.objects,
    ('recommend','*'): MatchestRecommendApp.objects,
    ('rank','app'): ApplicationTopApp.objects,
    ('rank','game'): GameTopApp.objects,
    ('rank','media'): MusicVideoTopApp.objects,
    ('rank','reading'): ReadingTopApp.objects,
    ('necessary','*'): necessary_listitem,
    ('hottest','*'): HottestRecommendApp.objects,
    ('homenew','*'): HomeNewRecommendApp.objects,
}


def get_listitem_by(list_type_detail):
    cls_mananger = None
    app_list = []
    if list_type_detail in listitem_objects_map:
        logger.info(str(list_type_detail))
        cls_mananger = listitem_objects_map[list_type_detail]
        app_list = cls_mananger.filter(sync_status=True, hided=False).order_by('order')
    else:
        list_type_all = list(list_type_detail)
        list_type_all[1] = '*'
        list_type_all = tuple(list_type_all)
        if list_type_all in listitem_objects_map:
            logger.info(str(list_type_all))
            cls_mananger = listitem_objects_map[list_type_all]
            app_list = cls_mananger.filter(sync_status=True, hided=False).order_by('order')
    return app_list


def parse_name_id(name_id):
    index = name_id.rfind('_')
    if index > 0:
        return (name_id[:index].decode('utf-8'), name_id[index+1:])
    else:
        return []

#first column: app_name_id
#second column: times
def combine_beluga_data(beluga_data_source):
    data_detail = beluga_data_source.get('detail', [])
    data_outer = beluga_data_source.get('outer', [])
    detail_dict = {}

    for item in data_detail:
        tmp_dict = {}
        app_name_id = item[0]
        times = item[1]
        parsed_data = parse_name_id(item[0])
        if parsed_data:
            name,app_id = parsed_data
        else:
            continue
        try:
            app_id = int(app_id)
            times = int(times)
            if app_id in detail_dict:
                detail_dict[app_id]['detail_times'] += times
                detail_dict[app_id]['total_times'] += times
            else:
                tmp_dict['name'] = name
                tmp_dict['id'] = app_id
                tmp_dict['detail_times'] = times
                tmp_dict['outer_times'] = 0
                tmp_dict['total_times'] = times
                detail_dict[app_id] = tmp_dict
        except Exception,e:
            logger.error(str(e))
            print e
    for item in data_outer:
        app_name_id = item[0]
        times = item[1]
        parsed_data = parse_name_id(item[0])
        if parsed_data:
            name,app_id = parsed_data
        else:
            continue
        try:
            app_id = int(app_id)
            detail_item = detail_dict.get(app_id, {})
            times = int(times)
            if detail_item:
                detail_item['outer_times'] += times
                detail_item['total_times'] += times
                detail_dict[app_id] = detail_item
            else:
                detail_item = {}
                detail_item['name'] = name
                detail_item['id'] = app_id
                detail_item['outer_times'] = times
                detail_item['detail_times'] = 0
                detail_item['total_times'] = times
                detail_dict[app_id] = detail_item
        except Exception,e:
            logger.error(str(e))
            print e
    return detail_dict


def combine_source(sources):
    sources_dict = {'detail':[], 'outer':[]}
    for sour in sources:
        if isinstance(sour, dict):
            source_detail = sour.get('detail', None)
            source_outer = sour.get('outer', None)
            if source_detail and source_outer:
                if source_detail != 'none' and source_detail not in sources_dict['detail']:
                    sources_dict['detail'].append(source_detail)
                if source_outer != 'none' and source_outer not in sources_dict['outer']:
                    sources_dict['outer'].append(source_outer)
    return sources_dict


#params:
# key:sources, versions, begin_date, end_date
def get_basic_download(params):
    sources_list = []
    list_type = params.get('list_type', None)
    list_detail = params.get('list_detail', None)
    logger.info(str(params))

    if not list_type or list_type not in sources_detail_map:
        return []
    sources_detail = sources_detail_map[list_type]
    if not list_detail:
        iter_sources = [source for source in sources_detail.values()]
        list_detail = '*'
        for source in iter_sources:
            sources_list.append(source)
    elif list_detail not in sources_detail:
        return []
    else:
        sources_list.append(sources_detail[list_detail])

    list_type_detail = (list_type, list_detail)
    #logger.info(str(sources_list))

    listitem_data_source = get_listitem_by(list_type_detail)
    #logger.info(str(listitem_data_source))

    if not listitem_data_source:
        return []
    sources_dict = combine_source(sources_list)

    logger.info(str(sources_dict))
    beluga_data_source = {}
    for key in sources_dict:
        if sources_dict[key]:
            params['sources'] = sources_dict[key]
            beluga_data_source.update({key:store.get_download_times(params)})
        else:
            beluga_data_source.update({key:[]})

    #logger.info(str(beluga_data_source))
    combined_beluga_data_dict = combine_beluga_data(beluga_data_source)
    extra_beluga_data_dict = combined_beluga_data_dict.copy()
    combined_data = []
    for item in listitem_data_source:
        app_id = item.app_id
        order = item.order
        if app_id in combined_beluga_data_dict:
            beluga_item = combined_beluga_data_dict[app_id]
            beluga_item['order'] = order
            combined_data.append(beluga_item)
            del extra_beluga_data_dict[app_id]
        else:
            beluga_item = {}
            beluga_item['name'] = item.app.name
            beluga_item['id'] = app_id
            beluga_item['detail_times'] = 0
            beluga_item['outer_times'] = 0
            beluga_item['total_times'] = 0
            beluga_item['order'] = order
            combined_data.append(beluga_item)

    for k,v in extra_beluga_data_dict.iteritems():
        v['order'] = -1
        combined_data.append(v)

    #logger.info(str(combined_data))
    return combined_data



def get_basic_search(params):
    list_type = params.get('list_type', None)
    list_detail = params.get('list_detail', None)
    basic_data = []
    if list_type == 'search' and list_detail in sources_search_map:
        params['sources'] = sources_search_map[list_detail]
        if 'search_search' in params['sources']:
            params['limits'] = 0
        #logger.info(params)
        basic_data = store.get_rankinglist_times(params)
        #logger.info(basic_data)

    sorted_list = []
    parsed_dict = {}
    i = 1
    for item in basic_data:
        app_name_id = item[0].decode('utf-8')
        times = item[1]
        index = app_name_id.rfind('_')
        if index > 0:
            name, app_id = app_name_id[:index], app_name_id[index+1:]
        else:
            name, app_id = app_name_id, -1

        try:
            app_id = int(app_id)
        except:
            continue

        row_dict = {}
        row_dict['id'] = app_id
        row_dict['name'] = name
        row_dict['total_times'] = int(times)
        if app_id == -1:
            app_id = i
            i += 1
        if app_id in parsed_dict:
            parsed_dict[app_id]['total_times'] += row_dict['total_times']
        else:
            parsed_dict[app_id] = row_dict

    sorted_list = [parsed_dict[appid] for appid in sorted(parsed_dict.keys())]
    return sorted_list
