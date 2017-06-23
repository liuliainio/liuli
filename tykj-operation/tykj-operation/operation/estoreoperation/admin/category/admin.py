from estorecore.admin.sites import custom_site
from estoreoperation.app.admin import CategoryAdmin
from estoreoperation.admin.category.models import AppCategory

custom_site.register(AppCategory, CategoryAdmin)
