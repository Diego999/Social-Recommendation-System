from events.models import *
from app_config import *
from matrix import *


class Recommendation:
    """
    Class allows every necessary operations to compute a recommendation
    """

    EMPTY_CASE = -1

    def __init__(self):
        self.r = Matrix(User.objects.all(), Event.objects.all(), int, Recommendation.EMPTY_CASE)
        self.f = Matrix(Event.objects.all(), Feature.objects.all(), bool)
        self.p = Matrix(User.objects.all(), Feature.objects.all(), int)

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
                if self.r[u, i] > Pt:
                    for f in self.f.get_cols():
                        if self.f[i, f]:
                            self.p[u, f] += 1
        for fu in FeatureUser.objects.all():
            self.p[fu.user, fu.feature] += 1

    def get_matrix_r(self):
        return self.r

    def get_matrix_f(self):
        return self.f

    def get_matrix_p(self):
        return self.p
