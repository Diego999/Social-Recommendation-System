from pyfb import Pyfb
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from app_config import FACEBOOK_APP_ID, FACEBOOK_SECRET_KEY, FACEBOOK_REDIRECT_URL
from Graph import Graph
from functions import compute_facebook_user_correlation, user_process, list_feature_user


# The code of this method is from https://github.com/jmg/pyfb
def facebook_login(request):
    facebook = Pyfb(FACEBOOK_APP_ID)
    return HttpResponseRedirect(facebook.get_auth_code_url(redirect_uri=FACEBOOK_REDIRECT_URL))


# A part of this code is from https://github.com/jmg/pyfb
def facebook_login_success(request):
    code = request.GET.get('code')
    facebook = Pyfb(FACEBOOK_APP_ID)
    request.session['tokenFB'] = facebook.get_access_token(FACEBOOK_SECRET_KEY, code,
                                                           redirect_uri=FACEBOOK_REDIRECT_URL)
    user_process(request.session.get('tokenFB'))
    return HttpResponseRedirect(reverse('main.views.manage'))


def facebook_analysis(request):
    graph = Graph(request.session['tokenFB'])
    me, friends = graph.fetch_information()
    compute_facebook_user_correlation(me, friends, graph)
    return facebook_info(request)


def facebook_info(request):
    context = {
        'info': list_feature_user(Graph(request.session['tokenFB']))
    }
    return render_to_response('facebook/info.html', context)



