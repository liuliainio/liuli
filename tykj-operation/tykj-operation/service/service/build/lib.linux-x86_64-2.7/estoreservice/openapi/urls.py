from django.conf.urls.defaults import patterns, url
from views import update_service, app_categories, app_category_apps, app_list_apps, \
    app_subjects, app_subject_apps, app_info, app_related_apps, app_developer_apps, \
    app_updates, app_updates2, app_reviews, app_download, app_download_from_dolphin, client_activate, search_hot_keywords, \
    login_pictures, activities, feedbacks, crash_report, push_notification_messages, get_app_reviews, post_app_review

urlpatterns = patterns('',
                       # does not used in furture version
                       url(r'^updateservice.json', update_service),
                       url(r'^crash_report/$', crash_report),
                       url(r'^notification/android/messages.json',
                           push_notification_messages),
                       url(r'^login-pictures.json', login_pictures),
                       url(r'^activities.json', activities),
                       url(r'^feedbacks.json', feedbacks),
                       url(r'^app/categories.json', app_categories),
                       url(r'^app/category/apps.json', app_category_apps),
                       url(r'^app/list/apps.json', app_list_apps),
                       url(r'^app/subjects.json', app_subjects),
                       url(r'^app/subject/apps.json', app_subject_apps),
                       url(r'^app/info.json', app_info),
                       url(r'^app/relatedapps.json', app_related_apps),
                       url(r'^app/developerapps.json', app_developer_apps),
                       url(r'^app/updates.json', app_updates),
                       url(r'^app/updates2.json', app_updates2),
                       #    url(r'^app/reviews.json', app_reviews),
                       url(r'^app/search/hot-keywords.json',
                           search_hot_keywords),
                       url(r'^app/download/app.json', app_download),
                       url(r'^app/download/package.json', app_download),
                       url(r'^app/download/fromdolphin',
                           app_download_from_dolphin),
                       url(r'^app/getreviews.json', get_app_reviews),
                       url(r'^app/postreview.json', post_app_review),

                       url(r'^activate.json', client_activate),
                      )
