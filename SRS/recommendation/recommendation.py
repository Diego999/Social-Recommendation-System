from numpy import zeros
from events.models import *
from app_config import *


class Recommendation:
    """
    Class allows every necessary operations to compute a recommendation
    """
    def __init__(self):
        self.users = User.objects.all()
        self.users_index = [u for u in self.users]
        self.events = Event.objects.all()
        self.events_index = [e for e in self.events]
        self.features = Feature.objects.all()
        self.features_index = [f for f in self.features]

        self.r = zeros(shape=(len(self.users), len(self.events))).astype(int)
        self.f = zeros(shape=(len(self.events), len(self.features))).astype(bool)
        self.p = zeros(shape=(len(self.users), len(self.features))).astype(int)

    def init_basic_matrix(self):
        """
        Initialize the basic matrix (R, F, P)
        """
        self.create_matrix_r()
        self.create_matrix_f()
        self.create_matrix_p()

    def create_matrix_r(self):
        """
        Initialize the matrix R (User - Item)
        """
        for ur in Rating.objects.all():
            self.r[self.users_index.index(self.users.get(id=ur.user_id)),
                   self.events_index.index(self.events.get(id=ur.event_id))] = ur.rating

    def create_matrix_f(self):
        """
        Initialize the matrix F (Item - Feature)
        """
        for ef in EventFeature.objects.all():
            self.f[self.events_index.index(self.events.get(id=ef.event_id)),
                   self.features_index.index(self.features.get(id=ef.feature_id))] = True

    def create_matrix_p(self):
        """
        Initialize the matrix P (User - Feature). Warning : You have to initialize first R & F
        """
        for u in range(0, self.r.shape[0]):
            for i in range(0, self.r.shape[1]):
                if self.r[u, i] > Pt:
                    for f in range(0, self.f.shape[1]):
                        if self.f[i, f]:
                            self.p[u, f] += 1
        for fu in FeatureUser.objects.all():
            self.p[self.users_index.index(self.users.get(id=fu.user_id)),
                   self.features_index.index(self.features.get(id=fu.feature_id))] += 1
