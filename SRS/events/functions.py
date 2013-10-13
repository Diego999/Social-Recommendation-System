import urllib2
import json
import re
from models import Event, Category

def create_urls(begin, end):
    """
    Generate all the available url for the API to fetch the event
    """
    url_template = 'https://www.gokera.ch/api/1.0/events/all_by_date?currentPage=%s&apiKey=000'

    out = list()
    for i in range(begin, end+1):
        out.append(url_template % i)
    return out

def fetch__update_database():
    """
    Fetch & Update the database.
    Return a tuple : (categoriesUpdated, categoriesInserted, eventsUpdated, eventsInserted)
    """
    categories_updated = list()
    categories_inserted = list()
    events_updated = list()
    events_inserted = list()

    for u in create_urls(1, json.load(urllib2.urlopen(create_urls(1, 1)[0]))['totalPages']):
        for e in json.load(urllib2.urlopen(u))['events']:
            cat = None
            try:
                cat = Category.objects.filter(external_id__exact=e['category']['externalId'])[0]

                if cat.name != e['category']['name']:
                    cat.name = e['category']['name']
                    categories_updated.append(cat.name)
            except IndexError:
                cat = Category(external_id=e['category']['externalId'], name=e['category']['name'])
                categories_inserted.append(cat.name)
            cat.save()

            event = None
            description = re.sub('\\n', '', e['description'])
            try:
                event = Event.objects.filter(external_id__exact=e['externalId'])[0]
                if unicode(event.category.external_id) != e['category']['externalId'] or unicode(event.external_id) != e['externalId'] or unicode(event.name) != e['name'] or unicode(event.website) != e['website'] or unicode(event.description) != description:
                    event.category = cat
                    event.external_id = e['externalId']
                    event.name = e['name']
                    event.website = e['website']
                    event.description = description
                    events_updated.append(event.name)
                    
            except IndexError:
                event = Event(category=cat,
                              external_id=e['externalId'],
                              name=e['name'],
                              website=e['website'],
                              description=description)

                events_inserted.append(event.name)

            event.save()
    return categories_updated, categories_inserted, events_updated, events_inserted

def get_all_categories():
    """
    Return all the existing categories in the fetch__update_database
    """
    return Category.objects.all().order_by('name')

def add_event_process(post):
    """
    Add the event past by POST method.
    Return event's unicode
    """
    cat = Category.objects.filter(external_id__exact=post['category'])[0]
    e = Event(category=cat,
              external_id=post['external_id'],
              name=post['name'],
              description=post['description'],
              website=post['website']
              )
    e.save()
    return e.__unicode__()