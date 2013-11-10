import urllib2
import json
import re
from models import Event, Category, Rating, RatingValue
from FBGraph.Graph import Graph
from FBGraph.models import User
from app_config import GOKERA_API
from django.core.exceptions import ObjectDoesNotExist
from multiprocessing import cpu_count
from event_analyse.functions import start_threads


def create_urls(begin, end):
    """
    Generate all the available url for the API to fetch the event
    Return : List with all the urls
    """
    url_template = GOKERA_API

    out = list()
    for i in range(begin, end+1):
        out.append(url_template % i)
    return out


def fetch__update_database():
    """
    Fetch & Update the database.
    Return : tuple (categoriesUpdated, categoriesInserted, eventsUpdated, eventsInserted)
    """
    categories_updated = list()
    categories_inserted = list()
    events_updated = list()
    events_inserted = list()

    urls = create_urls(1, json.load(urllib2.urlopen(create_urls(1, 1)[0]))['totalPages'])

    nb_core = cpu_count()
    nb_urls = len(urls)
    nb_urls_thread = nb_urls/nb_core
    urls_thread = []

    for i in range(nb_core-1):
        urls_thread.append(urls[i*nb_urls_thread:(i+1)*nb_urls_thread])
    urls_thread.append(urls_thread[(nb_core-1)*nb_urls_thread:])

    start_threads(nb_core, update_database, urls_thread, categories_updated, categories_inserted, events_updated,
                  events_inserted)

    return categories_updated, categories_inserted, events_updated, events_inserted


def update_database(categories_updated, categories_inserted, events_updated, events_inserted, urls):
    """
    Thread that update the database with a list of urls
    """
    for u in urls:
        for e in json.load(urllib2.urlopen(u))['events']:
            cat = None
            try:
                cat = Category.objects.get(external_id=e['category']['externalId'])

                if cat.name != e['category']['name']:
                    cat.name = e['category']['name']
                    categories_updated.append(cat.name)
            except ObjectDoesNotExist:
                cat = Category(external_id=e['category']['externalId'], name=e['category']['name'])
                categories_inserted.append(cat.name)
            cat.save()

            event = None
            description = re.sub('\\n', '', e['description'])
            try:
                event = Event.objects.get(external_id=e['externalId'])
                if unicode(event.category.external_id) != e['category']['externalId'] \
                    or unicode(event.external_id) != e['externalId'] \
                    or unicode(event.name) != e['name'] \
                    or unicode(event.website) != e['website'] \
                    or unicode(event.description) != description:

                    event.category = cat
                    event.external_id = e['externalId']
                    event.name = e['name']
                    event.website = e['website']
                    event.description = description
                    events_updated.append(event.name)

            except ObjectDoesNotExist:
                event = Event(category=cat,
                              external_id=e['externalId'],
                              name=e['name'],
                              website=e['website'],
                              description=description)

                events_inserted.append(event.name)

            event.save()


def get_all_categories():
    """
    Return all the existing categories in the fetch__update_database
    Return : List of Category objects
    """
    return Category.objects.all().order_by('name')


def add_event_process(post):
    """
    Add the event past by POST method.
    Return : event's unicode
    """
    cat = Category.objects.get(external_id=post['category'])
    e = Event(category=cat,
              external_id=post['external_id'],
              name=post['name'],
              description=post['description'],
              website=post['website']
              )
    e.save()
    return e.__unicode__()


def get_all_event_sorted(token):
    """
    Get all the events in a dictionary : Rated and Unrated according to the user. For the rated events,
    you'll have if the current user likes or dislikes
    Return : Dictionary {rated, unrated}
    rated : List[List of Event object, Like or Dislike]
    unrated : List[List of Event objects]
    """
    current_user = User.objects.get(external_id=Graph(token).get_me()['id'])

    rated_events = list()
    for r in Rating.objects.filter(user=current_user):
        rated_events.append([Event.objects.get(id=r.event.id), 'Like' if r.rating == RatingValue.LIKE else 'Dislike'])
    unrated_events = Event.objects.exclude(id__in=[r[0].id for r in rated_events])

    return {'rated': rated_events,
            'unrated': unrated_events}


def rate_event_process(external_id, rating, token):
    """
    Insert, Update or delete the event
    """
    if int(rating) == int(RatingValue.NEUTRAL):
        try:
            Rating.objects.get(event=Event.objects.get(external_id=external_id)).delete()
        except ObjectDoesNotExist:
            #  The value doesn't exist, so it's already deleted
            pass
    else:
        e = Event.objects.get(external_id=external_id)
        u = User.objects.get(external_id=Graph(token).get_me()['id'])
        r = None
        try:
            r = Rating.objects.get(event=e, user=u)
            r.rating = rating
        except ObjectDoesNotExist:
            r = Rating(event=e, user=u, rating=rating)
        r.save()


