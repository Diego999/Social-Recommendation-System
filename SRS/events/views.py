from django.shortcuts import render_to_response
from django.template import RequestContext
import functions

def addEvent(request):
    context = {
        'categories' : functions.getAllCategories()
    }
    return render_to_response('events/addEvent.html', context, context_instance=RequestContext(request))

def fetchDatabase(request):
    res = functions.fetchAndUpdateDatabase()
    context = {
        'data': {'Categories Updates':res[0],
                  'Categories Inserted':res[1],
                  'Events Updated':res[2],
                  'Events Inserted':res[3]}
    }
    return render_to_response('events/fetchDatabase.html', context)

def addEventProcess(request):
    res = functions.addEventProcess(request.POST)
    context = {
        'event' : res.split('\t')
    }
    return render_to_response('events/addEvent.html', context)