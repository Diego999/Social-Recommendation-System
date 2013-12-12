from django.shortcuts import render_to_response
from functions import *


def compute_recommendation(request):
    R = create_matrix_R()
    F = create_matrix__F()
    P = create_matrix_P(R, F)
    context = {
    }
    return render_to_response('recommendation/recommendation.html', context)

