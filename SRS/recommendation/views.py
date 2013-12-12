from django.shortcuts import render_to_response
from functions import *


def view_recommendation(request):
    compute_recommendation()
    context = {
    }
    return render_to_response('recommendation/recommendation.html', context)

