from django.shortcuts import render_to_response
import functions


def list_event_features(request):
    context = {
        'data': functions.get_list_event_features()
    }
    return render_to_response('event_analysis/list_event_features.html', context)


def event_analysis(request):
    functions.event_analysis()
    context = {}
    return render_to_response('main/manage.html', context)