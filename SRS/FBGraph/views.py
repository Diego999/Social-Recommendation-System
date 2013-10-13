from pyfb import Pyfb
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from settings import FACEBOOK_APP_ID, FACEBOOK_SECRET_KEY, FACEBOOK_REDIRECT_URL

#The code of this method is from https://github.com/jmg/pyfb
def facebook_login(request):
    facebook = Pyfb(FACEBOOK_APP_ID)
    return HttpResponseRedirect(facebook.get_auth_code_url(redirect_uri=FACEBOOK_REDIRECT_URL))

#A part of this code is from https://github.com/jmg/pyfb
def facebook_login_success(request):
    code = request.GET.get('code')
    facebook = Pyfb(FACEBOOK_APP_ID)
    facebook.get_access_token(FACEBOOK_SECRET_KEY, code, redirect_uri=FACEBOOK_REDIRECT_URL)

    request.session['nameFB'] = facebook.get_myself().name
    print facebook.get_myself()
    return HttpResponseRedirect(reverse('main.views.manage'))

def facebook_info(request):
    context = {
    }
    return render_to_response('facebook/info.html', context)



