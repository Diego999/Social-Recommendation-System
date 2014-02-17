from django.shortcuts import render_to_response
from FBGraph.Graph import Graph


def index(request):
    return render_to_response('main/index.html', {})


def manage(request):
    context = {
        'name': Graph(request.session.get('tokenFB')).get_me()['name']
    }
    return render_to_response('main/manage.html', context)
