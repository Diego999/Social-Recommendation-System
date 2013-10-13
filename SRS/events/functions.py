import urllib2
import json
import re
from models import Event, Category

def createUrls(begin, end):
    url_template = 'https://www.gokera.ch/api/1.0/events/all_by_date?currentPage=%s&apiKey=000'

    out = list()
    for i in range(begin, end+1):
        out.append(url_template % i)
    return out

def fetchAndUpdateDatabase():
    '''
    Fetch & Update the database.
    Return a tuple : (categoriesUpdated, categoriesInserted, eventsUpdated, eventsInserted)
    '''
    categoriesUpdated = list()
    categoriesInserted = list()
    eventsUpdated = list()
    eventsInserted = list()

    for u in createUrls(1, json.load(urllib2.urlopen(createUrls(1, 1)[0]))['totalPages']):
        for e in json.load(urllib2.urlopen(u))['events']:
            cat = None
            try:
                cat = Category.objects.filter(externalId__exact=e['category']['externalId'])[0]

                if cat.name != e['category']['name']:
                    cat.name = e['category']['name']
                    categoriesUpdated.append(cat.name)
            except IndexError:
                cat = Category(externalId=e['category']['externalId'], name=e['category']['name'])
                categoriesInserted.append(cat.name)
            cat.save()

            event = None
            description = re.sub('\\n', '', e['description'])
            try:
                event = Event.objects.filter(externalId__exact=e['externalId'])[0]
                if unicode(event.category.externalId) != e['category']['externalId'] or unicode(event.externalId) != e['externalId'] or unicode(event.name) != e['name'] or unicode(event.website) != e['website'] or unicode(event.description) != description:
                    event.category = cat
                    event.externalId = e['externalId']
                    event.name = e['name']
                    event.website = e['website']
                    event.description = description
                    eventsUpdated.append(event.name)
                    
            except IndexError:
                event = Event(category=cat,
                              externalId=e['externalId'],
                              name=e['name'],
                              website=e['website'],
                              description=description)

                eventsInserted.append(event.name)

            event.save()
    return (categoriesUpdated, categoriesInserted, eventsUpdated, eventsInserted)

def getAllCategories():
    return Category.objects.all().order_by('name')

def addEventProcess(post):
    '''
    Add the event past by POST method.
    Return event's unicode
    '''
    cat = Category.objects.filter(externalId__exact=post['category'])[0]
    e = Event(category=cat,
              externalId=post['externalId'],
              name=post['name'],
              description=post['description'],
              website=post['website']
              )
    e.save()
    return e.__unicode__()