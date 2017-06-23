from ajax_select import LookupChannel
from estoreoperation.app.models import AppVersion


class AppVersionLookUp(LookupChannel):

    search_field = 'version'
    model = AppVersion

    def get_query(self, q, request):
        """ return a query set searching for the query string q
            either implement this method yourself or set the search_field
            in the LookupChannel class definition
        """
        kwargs = {"%s__icontains" % self.search_field: q}
        related_id = request.GET.get('related_id')
        if related_id:
            kwargs['app__id'] = related_id
        return AppVersion.objects.filter(**kwargs).order_by(self.search_field)
