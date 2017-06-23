from syncto import sync_to_production
from syncfrom import sync_from_production

from estorecore.models.region import PhoneRegion
from estorecore.models.search import SearchKeyword,KeywordLocation
from estorecore.models.update import UpdateApp
from estorecore.models.push import Message
from estorecore.models.promotion import Activity, LoginPicture, Feedback, LocalEntry
from estorecore.models.app import Category, Application, CategoryFoucsImage, BootApp, TopApp, KuWanItem, \
        CategorySubject, CategoryRecommendApp, PreparedApp, AppReview, SubjectItem, AppList, AppListItem, AppMaskOff
from estorecore.datasync.modeladapter import register, adapters
from estorecore.servemodels import AppMongodbStorage, PromotionMongodbStorage, \
        SearchMongodbStorage, UpdateMongodbStorage, PushMongodbStorage, LocationMongodbStorage

register(Category, adapters.CategoryAdapter, {'db': AppMongodbStorage, 'table': 'categories'})
register(Application, adapters.ApplicationAdapter, {'db': AppMongodbStorage, 'table': 'apps'})
register(CategoryRecommendApp, adapters.RecommendAppAdapter, {'db': AppMongodbStorage, 'table': 'recommends'})
register(CategoryFoucsImage, adapters.FoucsImageAdapter, {'db': AppMongodbStorage, 'table': 'focus_images'})
register(CategorySubject, adapters.SubjectAdapter, {'db': AppMongodbStorage, 'table': 'subjects'})
register(TopApp, adapters.TopAppAdapter, {'db': AppMongodbStorage, 'table': 'tops'})
register(SubjectItem, adapters.SubjectItemAdapter, {'db': AppMongodbStorage, 'table': 'subject_apps'})
register(PreparedApp, adapters.PreparedAppAdapter, {'db': AppMongodbStorage, 'table': 'must_haves'})
register(BootApp, adapters.BootAppAdapter, {'db': AppMongodbStorage, 'table': 'bootapps'})
register(AppReview, adapters.AppReviewAdapter, {'db': AppMongodbStorage, 'table': 'reviews', 'method': 'get_need_sync_reviews'})
register(AppList, adapters.AppListAdapter, {'db': AppMongodbStorage, 'table': 'app_lists',})
register(AppListItem, adapters.AppListItemAdapter, {'db': AppMongodbStorage, 'table': 'app_list_items',})
register(KuWanItem, adapters.KuWanItemAdapter, {'db': AppMongodbStorage, 'table': 'kuwan_items'})
register(AppMaskOff, adapters.AppMaskOffAdapter, {'db': AppMongodbStorage, 'table': 'app_maskoff'})

register(Activity, adapters.ActivityAdapter, {'db': PromotionMongodbStorage, 'table': 'activities'})
register(LoginPicture, adapters.LoginPictureAdapter, {'db': PromotionMongodbStorage, 'table': 'login_pictures'})
register(LocalEntry, adapters.LocalEntryAdapter, {'db': PromotionMongodbStorage, 'table': 'local_entry'})
register(Feedback, adapters.FeedbackAdapter, {'db': PromotionMongodbStorage, 'method': 'get_need_sync_feedbacks'})

register(KeywordLocation, adapters.KeywordLocationAdapter, {'db': SearchMongodbStorage, 'table': 'search_keyword_ranking'})
register(SearchKeyword, adapters.SearchKeywordAdapter, {'db': SearchMongodbStorage, 'table': 'hot_keywords'})
register(PhoneRegion, adapters.PhoneRegionAdapter, {'db': LocationMongodbStorage, 'table': 'phone_region'})

register(UpdateApp, adapters.UpdateAppAdapter, {'db': UpdateMongodbStorage, 'table': 'update_apps'})
register(Message, adapters.PushMessageAdapter, {'db': PushMongodbStorage, 'table': 'messages'})
