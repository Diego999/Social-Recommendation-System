from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import RatingValue
import functions


def add_event(request):
    context = {
        'categories': functions.get_all_categories()
    }
    return render_to_response('events/add_event.html', context, context_instance=RequestContext(request))


def fetch_database(request):
    res = functions.fetch__update_database()
    context = {
        'data': {'Categories Updates': res[0],
                  'Categories Inserted': res[1],
                  'Events Updated': res[2],
                  'Events Inserted': res[3]}
    }
    return render_to_response('events/fetch_database.html', context)


def add_event_process(request):
    request.session['post'] = request.POST
    return HttpResponseRedirect(reverse('events.views.display_event_added'))


def display_event_added(request):
    res = functions.add_event_process(request.session.get('post'))
    context = {
        'event' : res.split('\t')
    }
    return render_to_response('events/add_event.html', context)


def list_events(request):
    res = functions.get_all_event_sorted(request.session.get('tokenFB'))  # To keep the rated first
    context = {
        'rated_events': res['rated'],
        'unrated_events': res['unrated'],
        'like': RatingValue.LIKE,
        'neutral': RatingValue.NEUTRAL,
        'dislike': RatingValue.DISLIKE
    }
    return render_to_response('events/list_events.html', context)


def rate_event(request, external_id, rating):
    functions.rate_event_process(external_id, rating, request.session.get('tokenFB'))
    return list_events(request)