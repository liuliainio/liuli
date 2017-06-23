import time
from django.conf import settings
from django.contrib import auth


class AutoLogout:

  def process_request(self, request):
    if not request.user.is_authenticated() :
      #Can't log out if not logged in
      return
    try:
      if 'last_logind' not in request.session.keys():
        request.session['last_logind'] = time.time()
      if time.time() - request.session['last_logind'] > settings.AUTO_LOGOUT_DELAY*3600*24:
        auth.logout(request)
        # request.session = {}
        del request.session['last_logind']
        return
    except Exception, e:
      print e
      pass