from recommendation import Recommendation
from events.models import EventFeature
from collections import OrderedDict


def compute_recommendation(user):
    recommendation = Recommendation()
    recommendation.init_basic_matrix()
    recommendation.init_frequency_matrix()
    recommendation.compute_matrix()
    return get_features_event(recommendation.compute_recommended_events(user))


def get_features_event(res):
    out = {}
    for e in res.keys():
        out[e] = (res[e], [(ef.feature.name, ef.tf_idf*ef.weight.weight, ef.weight.weight, ef.weight.name)
                        for ef in EventFeature.objects.filter(event__exact=e).order_by('-tf_idf')])
    return OrderedDict(sorted(out.items(), key=lambda t: t[1][0], reverse=True))