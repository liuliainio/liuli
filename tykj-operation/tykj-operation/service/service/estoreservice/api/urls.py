from django.conf.urls.defaults import patterns, url
from views.update import update_service
from views.app import app_categories,\
    app_category_tops,\
    app_category_apps,\
    app_category_focus_images,\
    app_list_apps,\
    app_subjects,\
    app_subject_apps,\
    app_info,\
    app_related_apps,\
    app_developer_apps,\
    app_recommends,\
    app_updates, \
    app_reviews, \
    app_download, \
    app_blacklist,\
    request_handler,\
    client_activate
from views.search import search_hot_keywords
from views.promotion import activities, login_pictures, feedbacks
from views.upload import crash_report
from views.push import push_notification_messages

urlpatterns = patterns('',
                       # does not used in furture version
                       url(r'^updateservice.json', update_service),
                       url(r'^crash_report/$', crash_report),
                       url(r'^notification/android/messages.json',
                           push_notification_messages),
                       url(r'^uploadapplist.json', app_updates),
                       url(r'^activities.json', activities),
                       url(r'^login-pictures.json', login_pictures),
                       url(r'^feedbacks.json/(?P<types>\w+)', feedbacks),
                       url(r'^feedbacks.json', feedbacks),
                       url(r'^app/categories.json', app_categories),
                       url(r'^app/category/apps.json', app_category_apps),
                       url(r'^app/category/focus-images.json',
                           app_category_focus_images),
                       url(r'^app/category/tops.json', app_category_tops),
                       url(r'^app/list/apps.json', app_list_apps),
                       url(r'^app/subjects.json', app_subjects),
                       url(r'^app/subject/apps.json',
                           app_subject_apps, {'version': 1}),
                       url(r'^app/subject/items.json',
                           app_subject_apps, {'version': 2}),
                       url(r'^app/info.json', app_info),
                       url(r'^app/relatedapps.json', app_related_apps),
                       url(r'^app/developerapps.json', app_developer_apps),
                       url(r'^app/recommends.json', app_recommends),
                       url(r'^app/updates.json', app_updates),
                       url(r'^app/reviews.json', app_reviews),
                       url(r'^app/search/hot-keywords.json',
                           search_hot_keywords),
                       url(r'^app/download/app.json', app_download),
                       url(r'^app/download/package.json', app_download),

                       url(r'^handler/([^/]*)/([^/]*)/(.*)$', request_handler),
                       url(r'^activate.json', client_activate),
                       url(r'^app/blacklist.json', app_blacklist),
                      )
