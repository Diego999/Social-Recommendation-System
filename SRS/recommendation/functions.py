from numpy import matrix, zeros, shape
from events.models import *
from app_config import *

users = User.objects.all()
users_index = [u for u in users]
events = Event.objects.all()
events_index = [e for e in events]
features = Feature.objects.all()
features_index = [f for f in features]


def create_matrix_R():
    R = zeros(shape=(len(users), len(events))).astype(int)
    for ur in Rating.objects.all():
        R[users_index.index(users.get(id=ur.user_id)), events_index.index(events.get(id=ur.event_id))] = ur.rating
    return R


def create_matrix__F():
    F = zeros(shape=(len(events), len(features))).astype(bool)
    for ef in EventFeature.objects.all():
        F[events_index.index(events.get(id=ef.event_id)), features_index.index(features.get(id=ef.feature_id))] = True
    return F


def create_matrix_P(R, F):
    P = zeros(shape=(len(users), len(features))).astype(int)
    for u in range(0, R.shape[0]):
        for i in range(0, R.shape[1]):
            if R[u, i] > Pt:
                for f in range(0, F.shape[1]):
                    if F[i, f]:
                        P[u, f] += 1
    for fu in FeatureUser.objects.all():
        P[users_index.index(users.get(id=fu.user_id)), features_index.index(features.get(id=fu.feature_id))] += 1
    return P