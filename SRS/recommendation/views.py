from django.shortcuts import render_to_response
from FBGraph.Graph import Graph
from functions import compute_recommendation
from events.models import User


def get_recommendation(request):
    context = {
        'data': compute_recommendation(User.objects.get(external_id=Graph(request.session['tokenFB']).get_me()['id']))
    }
    return render_to_response('recommendation/recommendation.html', context)

