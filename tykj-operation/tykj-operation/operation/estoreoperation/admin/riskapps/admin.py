from estorecore.admin.sites import custom_site
from estoreoperation.app.admin import ApplicationAdmin
from estoreoperation.admin.riskapps.models import RiskApp


class RiskAppAdmin(ApplicationAdmin):

    def has_add_permission(self, request):
        return False

    def has_sync_to_permission(self, request, obj=None):
        return False

custom_site.register(RiskApp, RiskAppAdmin)
