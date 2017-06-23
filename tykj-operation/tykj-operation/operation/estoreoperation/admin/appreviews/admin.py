from estorecore.admin.sites import custom_site
from estoreoperation.app.admin import AppReviewAdmin
from estoreoperation.admin.appreviews.models import ApplicationReview

custom_site.register(ApplicationReview, AppReviewAdmin)
