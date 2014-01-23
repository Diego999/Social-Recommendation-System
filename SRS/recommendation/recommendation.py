from events.models import Event, Feature, User, Rating, EventFeature, FeatureUser
from app_config import *
from matrix_2d import Matrix2D
from matrix_1d import Matrix1D
from numpy import log10, sqrt


class Recommendation:
    """
    Class allows every necessary operations to compute a recommendation
    """

    EMPTY_CASE = -1
    EPSILON = 1e-6
    DECIMALS_MATRIX_UU = 4

    @staticmethod
    def compare_float(a, b):
        return abs(a - b) < Recommendation.EPSILON

    def __init__(self):
        features = Feature.objects.all()
        users = User.objects.all()
        events = Event.objects.all()

        self.r = Matrix2D(users, events, int, Recommendation.EMPTY_CASE)
        self.f = Matrix2D(events, features, float, Recommendation.EMPTY_CASE)
        self.p = Matrix2D(users, features, float, 0)
        self.s = Matrix2D(users, features, float, 0)

        self.ff = Matrix2D(users, features, float, 0)
        self.uf = Matrix1D(features, int)
        self.iuf = Matrix1D(features, float)

        self.w = Matrix2D(users, features, float, Recommendation.EMPTY_CASE)
        self.uu = Matrix2D(users, users, float, Recommendation.EMPTY_CASE)

    def init_basic_matrix(self):
        """
        Initialize the basic matrix (R, F, P)
        """
        self.create_matrix_r()
        self.create_matrix_f()
        self.create_matrix_s()
        self.create_matrix_p()

    def init_frequency_matrix(self):
        """
        Create the FF, UF, IUF matrix
        """
        self.create_matrix_ff()
        self.create_matrix_uf()
        self.create_matrix_iuf()

    def compute_matrix(self):
        """
        Compute the matrix W and UU
        """
        self.compute_matrix_w()
        self.compute_matrix_uu()

    def compute_matrix_w(self):
        """
        Compute the Weighted matrix
        """
        for u in self.ff.get_rows():
            for f in self.ff.get_cols():
                self.w[u, f] = self.ff[u, f] * self.iuf[f] if not Recommendation.compare_float(self.iuf[f], 0.0) and not Recommendation.compare_float(self.ff[u, f], 0.0) else self.EMPTY_CASE

    def compute_matrix_uu(self):
        """
        Compute the User-User matrix
        """
        users_u = User.objects.all()
        # It's a symmetric matrix, we don't need to go through all values
        for uu in range(0, len(users_u)):
            u = users_u[uu]
            for vv in range(uu, len(users_u)):
                v = users_u[vv]
                if u.id == v.id:
                    self.uu[u, v] = Recommendation.EMPTY_CASE
                else:
                    x = []
                    for f in self.p.get_cols():
                        if not Recommendation.compare_float(self.p[u, f], 0.0) and self.p[u, f] > 0.0 and not Recommendation.compare_float(self.p[v, f], 0.0) and self.p[v, f] > 0.0:
                            x.append(f)
                    if len(x) > 0:
                        nominator = 0.0
                        wu2 = 0.0
                        wv2 = 0.0
                        for f in x:
                            if not Recommendation.compare_float(self.w[u, f], Recommendation.EMPTY_CASE) and not Recommendation.compare_float(self.w[v, f], Recommendation.EMPTY_CASE):
                                nominator += self.w[u, f]*self.w[v, f]
                                wu2 += self.w[u, f]*self.w[u, f]
                                wv2 += self.w[v, f]*self.w[v, f]
                        denominator = sqrt(wu2)*sqrt(wv2)
                        self.uu[u, v] = self.uu[v, u] = nominator/denominator if not Recommendation.compare_float(denominator, 0.0) else Recommendation.EMPTY_CASE

    def compute_recommended_events(self, user):
        """
        Compute the recommendation with the others matrix computed before
        """
        from collections import OrderedDict
        scores = {}
        for u in self.uu.get_cols():
            if not Recommendation.compare_float(self.uu[user, u], Recommendation.EMPTY_CASE):
                scores[u] = self.uu[user, u]

        scores = OrderedDict(sorted(scores.items(), key=lambda t: t[1]))

        keys = scores.keys()
        k_similar_users = set()
        j = 0
        for i in range(0, len(keys)):
            if j == K_NEAREST_NEIGHBOR:
                break
            k_similar_users.add(keys[i])
            if i+1 < len(keys):
                if Recommendation.compare_float(scores[keys[i]], scores[keys[i+1]]):
                    k_similar_users.add(keys[i+1])
            else:
                j += 1

        similar_events = set()
        for u in k_similar_users:
            for i in self.r.get_cols():
                if self.r[u, i] != Recommendation.EMPTY_CASE and self.r[user, i] == Recommendation.EMPTY_CASE:
                    similar_events.add(i)

        features_event = {}
        for e in similar_events:
            features_event[e] = set()
            for f in self.f.get_cols():
                if not Recommendation.compare_float(self.f[e, f], Recommendation.EMPTY_CASE):
                    features_event[e].add(f)

        feature_frequency = {}
        for f in features_event.values():
            for ff in f:
                if ff not in feature_frequency:
                    feature_frequency[ff] = 1
                else:
                    feature_frequency[ff] += 1

        final_score_event = {}
        for e in similar_events:
            final_score_event[e] = 0
            for f in features_event[e]:
                final_score_event[e] += feature_frequency[f]

        return OrderedDict(sorted(final_score_event.items(), key=lambda t: t[1], reverse=True)[:K_MOST_RECOMMENDED_EVENTS])

    def create_matrix_ff(self):
        """
        Create the Feature Frequency matrix
        """
        for u in self.p.get_rows():
            for f in self.p.get_cols():
                self.ff[u, f] = WEIGHT_FEATURE_EVENT*self.p[u, f] + WEIGHT_FEATURE_FB*self.s[u, f]

    def create_matrix_uf(self):
        """
        Create the User Frequency matrix
        """
        for f in self.p.get_cols():
            for u in self.p.get_rows():
                if not Recommendation.compare_float(self.ff[u, f], 0.0) and self.ff[u, f] > 0.0:
                    self.uf[f] += 1

    def create_matrix_iuf(self):
        """
        Create the Inverse User Frequency matrix
        """
        len_users = float(len(self.r.get_rows()))
        for f in self.uf.get_rows():
            self.iuf[f] = log10(len_users/float(self.uf[f])) if self.uf[f] != 0 else 0.0

    def create_matrix_r(self):
        """
        Initialize the matrix R (User - Item)
        """
        for ur in Rating.objects.all():
            self.r[ur.user, ur.event] = ur.rating

    def create_matrix_f(self):
        """
        Initialize the matrix F (Item - Feature)
        """
        for ef in EventFeature.objects.all():
            self.f[ef.event, ef.feature] = ef.tf_idf*ef.weight.weight

    def create_matrix_p(self):
        """
        Initialize the matrix P (User - Feature). Warning : You have to initialize first R & F
        """
        for u in self.r.get_rows():
            for i in self.r.get_cols():
                if self.r[u, i] != self.EMPTY_CASE and self.r[u, i] > Pt:
                    for f in self.f.get_cols():
                        if not Recommendation.compare_float(self.f[i, f], Recommendation.EMPTY_CASE):
                            self.p[u, f] += self.f[i, f]

    def create_matrix_s(self):
        """
        Create the social matrix
        """
        for fu in FeatureUser.objects.all():
            self.s[fu.user, fu.feature] = fu.weight

    def get_matrix_r(self):
        return self.r

    def get_matrix_f(self):
        return self.f

    def get_matrix_p(self):
        return self.p

    def get_matrix_s(self):
        return self.s

    def get_matrix_uf(self):
        return self.uf

    def get_matrix_iuf(self):
        return self.iuf

    def get_matrix_w(self):
        return self.w

    def get_matrix_ff(self):
        return self.ff

    def get_matrix_uu(self):
        return self.uu