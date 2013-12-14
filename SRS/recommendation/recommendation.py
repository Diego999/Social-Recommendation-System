from events.models import Event, Feature, User, Rating, EventFeature, FeatureUser
from app_config import *
from matrix_2d import Matrix2D
from matrix_1d import Matrix1D
from numpy import log10
from math import pow, sqrt

class Recommendation:
    """
    Class allows every necessary operations to compute a recommendation
    """

    EMPTY_CASE = -1

    def __init__(self):
        features = Feature.objects.all()
        users = User.objects.all()
        events = Event.objects.all()

        self.r = Matrix2D(users, events, int, Recommendation.EMPTY_CASE)
        self.f = Matrix2D(events, features, bool)
        self.p = Matrix2D(users, features, int)
        self.s = Matrix2D(users, features, bool)

        self.ffn = Matrix2D(users, features, float, Recommendation.EMPTY_CASE)
        self.ffs = Matrix2D(users, features, float, Recommendation.EMPTY_CASE)
        self.ff = Matrix2D(users, features, float, Recommendation.EMPTY_CASE)
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
        self.create_matrix_ffn()
        self.create_matrix_ffs()
        self.create_matrix_ff()
        self.create_matrix_uf()
        self.create_matrix_iuf()

    def compute_matrix_w(self):
        for u in self.ff.get_rows():
            for f in self.ff.get_cols():
                self.w[u, f] = self.ff[u, f] * self.iuf[f] if self.iuf[f] != self.EMPTY_CASE else self.EMPTY_CASE

    def compute_matrix_uu(self):
        users_u = User.objects.all()
        # It's a symmetric matrix, we don't need to go through all values
        for uu in range(0, len(users_u)):
            u = users_u[uu]
            for vv in range(uu, len(users_u)):
                v = users_u[vv]
                if u.id == v.id:
                    self.uu[u, v] = self.EMPTY_CASE
                else:
                    x = []
                    for f in self.p.get_cols():
                        if self.p[u, f] > 0 and self.p[v, f] > 0:
                            x.append(f)
                    nominator = 0.0
                    wu2 = 0.0
                    wv2 = 0.0
                    for f in x:
                        nominator += self.w[u, f]*self.w[v, f]
                        wu2 += pow(self.w[u, f], 2)
                        wv2 += pow(self.w[v, f], 2)
                    denominator = sqrt(wu2)*sqrt(wv2)
                    self.uu[u, v] = self.uu[v, u] = nominator/denominator

    def create_matrix_ffn(self):
        for ef in EventFeature.objects.all():
            val = ef.tf_idf*ef.weight.weight
            for u in self.r.get_rows():
                self.ffn[u, ef.feature] = val

    def create_matrix_ffs(self):
        for uf in FeatureUser.objects.all():
            self.ffs[uf.user, uf.feature] = uf.weight

    def create_matrix_ff(self):
        for u in self.p.get_rows():
            for f in self.p.get_cols():
                self.ff[u, f] = max(self.ffn[u, f], self.ffs[u, f])

    def create_matrix_uf(self):
        for f in self.p.get_cols():
            for u in self.p.get_rows():
                if self.p[u, f] > 0:
                    self.uf[f] += 1

    def create_matrix_iuf(self):
        len_users = float(len(self.r.get_rows()))
        for f in self.uf.get_rows():
            self.iuf[f] = log10(2*len_users/float(self.uf[f])) if self.uf[f] != 0 else self.EMPTY_CASE

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
            self.f[ef.event, ef.feature] = True

    def create_matrix_p(self):
        """
        Initialize the matrix P (User - Feature). Warning : You have to initialize first R & F
        """
        for u in self.r.get_rows():
            for i in self.r.get_cols():
                if self.r[u, i] != self.EMPTY_CASE and self.r[u, i] > Pt:
                    for f in self.f.get_cols():
                        if self.f[i, f]:
                            self.p[u, f] += 1
                        if self.s[u, f]:
                            self.p[u, f] += 1

    def create_matrix_s(self):
        for fu in FeatureUser.objects.all():
            self.s[fu.user, fu.feature] = True

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

    def get_matrix_ffn(self):
        return self.ffn

    def get_matrix_ffs(self):
        return self.ffs

    def get_matrix_ff(self):
        return self.ff

    def get_matrix_uu(self):
        return self.uu