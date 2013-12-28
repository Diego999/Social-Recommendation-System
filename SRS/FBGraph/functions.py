from models import *
from Graph import Graph
from django.core.exceptions import ObjectDoesNotExist
from event_analyse.tree_tagger import TreeTagger
from app_config import *
from events.models import Feature, FeatureUser
from multiprocessing import cpu_count
import threading


def user_process(_token):
    """
    Add the user if he's a new facebook user of the application. Otherwise, change the current values
    """

    me = Graph(_token).get_me()
    current_user = None
    try:
        current_user = User.objects.get(external_id=me['id'])
        current_user.name = me['name']
        current_user.token = _token
    except ObjectDoesNotExist:
        current_user = User(external_id=me['id'], name=me['name'], token=_token)

    current_user.save()


def get_synonym(word):
    """
    For now, it'll return a list with the same word because we don't have time to implement a synonym system
    """
    return [word]


def compute_facebook_user_correlation(me, friends, graph):
    """
    Compute the correlation between the features in the database and the feature that we can find in the
    facebook user data and his friends
    """
    my_features = search_and_extract_key_words(me, [f.name for f in Feature.objects.all()])
    if my_features is not None and len(my_features) > 0:
        update_database_user_feature(graph, my_features, WEIGHT_FEATURE_USER_FB_DATA)

    friends_to_keep = []

    nb_core = cpu_count()
    nb_friends = len(friends)
    nb_friends_thread = nb_friends/nb_core
    friends_thread = []

    for i in range(nb_core-1):
        friends_thread.append(friends[i*nb_friends_thread:(i+1)*nb_friends_thread])
    friends_thread.append(friends[(nb_core-1)*nb_friends_thread:])

    start_threads(nb_core, start_extract_key_words, friends_thread, friends_to_keep)
    #MonoThread - start_extract_key_words(friends_to_keep, friends)

    if len(friends_to_keep) > 0:
        friends_sorted = []
        for i in range(0, len(friends_to_keep)):
            friends_sorted.append((friends_to_keep[i][0], friends_to_keep[i][0].get_average_absolute_deviation(graph), friends_to_keep[i][1]))
        friends_sorted = sorted(friends_sorted, key=lambda x: x[1])[:K_MOST_ACTIVE_FB_USER]

        avg_avg = 0.0
        for f in friends_sorted:
            avg_avg += f[0].get_average_between_post()
        avg_avg /= float(len(friends_sorted))

        for f in friends_sorted:
            update_database_user_feature(graph, f[2], min(1.0, f[0].get_average_between_post()/avg_avg))


def start_threads(nb_core, fct, tab, *args):
    """
    Starts as many thread as number of cores of the machine
    """
    threads = []
    for i in range(nb_core):
        thread = threading.Thread(target=fct, args=args + (tab[i],))
        threads.append(thread)
        thread.start()

    for t in threads:
        t.join()


def start_extract_key_words(friends_to_keep, friends):
    features = [f.name for f in Feature.objects.all()]
    for i in range(0, len(friends)):
        res = search_and_extract_key_words(friends[i], features)
        if res is not None:
            friends_to_keep.append((friends[i], res))


def search_and_extract_key_words(user, features):
    """
    Search and extract keywords from a user and compare them with the database features.
    If the intersection of both sets is None, return None otherwise return the intersection
    """
    f_features = []
    tagger = TreeTagger()
    for g in user.get_groups():
        f_features += extract_key_words(tagger, [g.get_name(), g.get_description()])
    for p in user.get_pages():
        f_features += extract_key_words(tagger, [p.get_name(), p.get_description()])

    keyword_in_both_features = []
    for f in f_features:
        for s in get_synonym(f):
            if s in features and s not in keyword_in_both_features:
                keyword_in_both_features.append(f)
                break

    return keyword_in_both_features if len(keyword_in_both_features) > 0 else None


def extract_key_words(tagger, texts):
    """
    Extract keywords in texts and add them uniquely in f_features
    """
    list_tags = []
    for t in texts:
        list_tags += tagger.tag_text(t, FILTER_TREE_TAGGER)

    features = []
    for t in list_tags:
        if t not in features:
            features.append(t)
    return features


def update_database_user_feature(graph, features, w):
    """
    Insert into the database the features and their weight, related of the user
    """
    u = User.objects.get(external_id=graph.get_me()['id'])
    try:
        for f in FeatureUser.objects.filter(user=u):
            f.delete()
    except ObjectDoesNotExist:
        #  The value doesn't exist, so it's already deleted
        pass

    for f in features:
        FeatureUser(user=u, weight=w, feature=Feature.objects.get(name__exact=f)).save()


def list_feature_user(graph):
    out = []
    try:
        for fu in FeatureUser.objects.filter(user=User.objects.get(external_id=graph.get_me()['id'])):
            out.append((fu.feature.name, fu.weight))
    except:
        pass
    return out