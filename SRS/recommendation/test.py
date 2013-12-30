from events.models import *
from matrix_1d import *
from matrix_2d import *
from collections import OrderedDict

"""There is a bug with mongo-engine so to execute a unit test with it, it's not very easy.
Is to call the class inside a function. The data used will be those of the production"""

def run_test():
    rec = RecommendationTest1()
    rec.setUp()
    rec.test_RFSP()
    rec.test_FF_UF_IUF()
    rec.test_W_UU()
    rec.test_final()

    rec = RecommendationTest2()
    rec.setUp()
    rec.test_RFSP()
    rec.test_FF_UF_IUF()
    rec.test_W_UU()
    rec.test_final()


def compare_list(l1, l2):
    if len(l1) != len(l2):
        return False

    from recommendation import Recommendation
    try:
        isSameSize = True
        for ll1 in l1:
            for ll2 in l2:
                isSameSize &= len(ll1) == len(ll2)
        if not isSameSize:
            return False

        for i in range(0, len(l1)):
            for j in range(0, len(l1[0])):
                if not Recommendation.compare_float(l1[i][j], l2[i][j]):
                    print '(', i, ';', j, ') ', l1[i][j], ' not eq ', l2[i][j]
                    return False
    except:
        for i in range(0, len(l1)):
            if not Recommendation.compare_float(l1[i], l2[i]):
                print '(', i, ') ', l1[i], ' not eq ', l2[i]
                return False
    return True


def transform_matrix_list(m):
    out = list()
    rows = m.get_rows()
    if isinstance(m, Matrix1D):
        for i in range(0, len(m.get_rows())):
            out.append(m[rows[i]])
    elif isinstance(m, Matrix2D):
        cols = m.get_cols()
        for i in range(0, len(m.get_rows())):
            out.append(list())
            for j in range(0, len(m.get_cols())):
                out[i].append(m[rows[i], cols[j]])
    return out


def clean():
    for u in User.objects.all():
        u.delete()
    for f in Feature.objects.all():
        f.delete()
    for uf in FeatureUser.objects.all():
        uf.delete()
    for fe in EventFeature.objects.all():
        fe.delete()
    for w in Weight.objects.all():
        w.delete()
    for c in Category.objects.all():
        c.delete()
    for r in Rating.objects.all():
        r.delete()
    for e in Event.objects.all():
        e.delete()


def compare_ordered_dict(d1, d2):
    if len(d1) != len(d2):
        return False

    keys1 = d1.keys()
    keys2 = d2.keys()
    values1 = d1.values()
    values2 = d2.values()
    for i in range(0, len(keys1)):
        if keys1[i] != keys2[i]:
            return False
        if values1[i] != values2[i]:
            return False
    return True


class RecommendationTest1:

    def setUp(self):
        clean()

        c = Category(name="C", external_id="1")
        w = Weight(name="t", weight=1.0)
        w.save()
        c.save()

        for i in range(0, 3):
            User(name="U"+str(i), external_id=str(i), token="t"+str(i)).save()
        users = User.objects.all()
        for i in range(0, 5):
            Feature(name="F"+str(i)).save()
        features = Feature.objects.all()
        for i in range(0, 5):
            Event(category=c, external_id=str(i), name='E'+str(i), website='', description='').save()
        events = Event.objects.all()

        Rating(event=events[0], user=users[0], rating=1).save()
        Rating(event=events[1], user=users[0], rating=2).save()
        Rating(event=events[2], user=users[0], rating=4).save()
        Rating(event=events[3], user=users[0], rating=5).save()
        Rating(event=events[4], user=users[0], rating=3).save()

        Rating(event=events[0], user=users[1], rating=3).save()
        Rating(event=events[1], user=users[1], rating=2).save()
        Rating(event=events[2], user=users[1], rating=5).save()

        Rating(event=events[0], user=users[2], rating=1).save()
        Rating(event=events[1], user=users[2], rating=4).save()
        Rating(event=events[4], user=users[2], rating=3).save()

        EventFeature(event=events[0], feature=features[0], tf_idf=0.2, weight=w).save()
        EventFeature(event=events[0], feature=features[2], tf_idf=0.8, weight=w).save()

        EventFeature(event=events[1], feature=features[1], tf_idf=0.8, weight=w).save()
        EventFeature(event=events[1], feature=features[2], tf_idf=1.0, weight=w).save()
        EventFeature(event=events[1], feature=features[4], tf_idf=0.3, weight=w).save()

        EventFeature(event=events[2], feature=features[0], tf_idf=1.0, weight=w).save()
        EventFeature(event=events[2], feature=features[2], tf_idf=0.3, weight=w).save()

        EventFeature(event=events[3], feature=features[1], tf_idf=0.2, weight=w).save()
        EventFeature(event=events[3], feature=features[3], tf_idf=0.4, weight=w).save()

        EventFeature(event=events[4], feature=features[3], tf_idf=0.8, weight=w).save()

        FeatureUser(user=users[0], feature=features[1], weight=0.4).save()
        FeatureUser(user=users[0], feature=features[3], weight=0.8).save()
        FeatureUser(user=users[0], feature=features[4], weight=0.3).save()

        FeatureUser(user=users[1], feature=features[0], weight=1.0).save()
        FeatureUser(user=users[1], feature=features[2], weight=0.5).save()

        FeatureUser(user=users[2], feature=features[1], weight=0.2).save()
        FeatureUser(user=users[2], feature=features[4], weight=0.6).save()

        from recommendation import Recommendation
        self.recommendation = Recommendation()

    def test_RFSP(self):
        RR = [[1, 2, 4, 5, 3],[3, 2, 5, -1, -1],[1, 4, -1, -1, 3]]
        FF = [[0.2, -1, 0.8, -1, -1],[-1, 0.8, 1, -1, 0.3],[1, -1, 0.3, -1, -1],[-1, 0.2, -1, 0.4, -1],[-1, -1, -1, 0.8, -1]]
        SS = [[0, 0.4, 0, 0.8, 0.3],[1, 0, 0.5, 0, 0],[0, 0.2, 0, 0, 0.6]]
        PP = [[1, 0.2, 0.3, 1.2, 0],[1.2, 0, 1.1, 0, 0],[0, 0.8, 1, 0.8, 0.3]]

        self.recommendation.init_basic_matrix()
        if not compare_list(RR, transform_matrix_list(self.recommendation.get_matrix_r())):
            print 'error RR test_RFSP'
            print RR, '\n', transform_matrix_list(self.recommendation.get_matrix_r())
        if not compare_list(FF, transform_matrix_list(self.recommendation.get_matrix_f())):
            print 'error FF test_RFSP'
            print FF, '\n', transform_matrix_list(self.recommendation.get_matrix_f())
        if not compare_list(SS, transform_matrix_list(self.recommendation.get_matrix_s())):
            print 'error SS test_RFSP'
            print SS, '\n', transform_matrix_list(self.recommendation.get_matrix_s())
        if not compare_list(PP, transform_matrix_list(self.recommendation.get_matrix_p())):
            print 'error PP test_RFSP'
            print PP, '\n', transform_matrix_list(self.recommendation.get_matrix_p())

    def test_FF_UF_IUF(self):
        FF = [[1, 0.6, 0.3, 2.0, 0.3],[2.2, 0, 1.6, 0, 0],[0, 1.0, 1, 0.8, 0.9]]
        UF = [2, 2, 3, 2, 2]
        IUF = [0.176091259056, 0.176091259056, 0.0, 0.176091259056, 0.176091259056]

        self.recommendation.init_frequency_matrix()
        if not compare_list(FF, transform_matrix_list(self.recommendation.get_matrix_ff())):
            print 'error FF test_RFSP'
            print FF, '\n', transform_matrix_list(self.recommendation.get_matrix_ff())
        if not compare_list(UF, transform_matrix_list(self.recommendation.get_matrix_uf())):
            print 'error UF test_RFSP'
            print UF, '\n', transform_matrix_list(self.recommendation.get_matrix_uf())
        if not compare_list(IUF, transform_matrix_list(self.recommendation.get_matrix_iuf())):
            print 'error IUF test_RFSP'
            print IUF, '\n', transform_matrix_list(self.recommendation.get_matrix_iuf())

    def test_W_UU(self):
        W = [[0.176091259056, 0.105654755433, -1, 0.352182518111, 0.0528273777167],[0.387400769922, -1, -1, -1, -1],[-1, 0.176091259056, -1, 0.140873007245, 0.15848213315]]
        UU = [[-1, 1.0, 0.822730338093],[1.0, -1, -1],[0.822730338093, -1, -1]]

        self.recommendation.compute_matrix_w()
        self.recommendation.compute_matrix_uu()
        if not compare_list(W, transform_matrix_list(self.recommendation.get_matrix_w())):
            print 'error W test_RFSP'
            print W, '\n', transform_matrix_list(self.recommendation.get_matrix_w())
        if not compare_list(UU, transform_matrix_list(self.recommendation.get_matrix_uu())):
            print 'error UU test_RFSP'
            print UU, '\n', transform_matrix_list(self.recommendation.get_matrix_uu())

    def test_final(self):
        events = Event.objects.all()
        res = {events[3]: 3, events[4]: 2}
        res = OrderedDict(sorted(res.items(), key=lambda t: t[1], reverse=True))

        if not compare_ordered_dict(self.recommendation.compute_recommended_events(User.objects.all()[1]), res):
            print 'error final result'
            print res
            print self.recommendation.compute_recommended_events(User.objects.all()[1])

class RecommendationTest2:

    def setUp(self):
        clean()

        c = Category(name="C", external_id="1")
        w = Weight(name="t", weight=1.0)
        w.save()
        c.save()

        for i in range(0, 4):
            User(name="U"+str(i), external_id=str(i), token="t"+str(i)).save()
        users = User.objects.all()
        for i in range(0, 4):
            Feature(name="F"+str(i)).save()
        features = Feature.objects.all()
        for i in range(0, 6):
            Event(category=c, external_id=str(i), name='E'+str(i), website='', description='').save()
        events = Event.objects.all()

        Rating(event=events[1], user=users[0], rating=4).save()
        Rating(event=events[4], user=users[0], rating=5).save()

        Rating(event=events[1], user=users[1], rating=3).save()
        Rating(event=events[3], user=users[1], rating=4).save()

        Rating(event=events[5], user=users[2], rating=4).save()

        Rating(event=events[0], user=users[3], rating=5).save()
        Rating(event=events[2], user=users[3], rating=3).save()

        EventFeature(event=events[0], feature=features[1], tf_idf=1, weight=w).save()

        EventFeature(event=events[1], feature=features[0], tf_idf=1, weight=w).save()
        EventFeature(event=events[1], feature=features[1], tf_idf=1, weight=w).save()

        EventFeature(event=events[2], feature=features[1], tf_idf=1, weight=w).save()
        EventFeature(event=events[2], feature=features[2], tf_idf=1, weight=w).save()

        EventFeature(event=events[3], feature=features[1], tf_idf=1, weight=w).save()

        EventFeature(event=events[4], feature=features[0], tf_idf=1, weight=w).save()
        EventFeature(event=events[4], feature=features[1], tf_idf=1, weight=w).save()
        EventFeature(event=events[4], feature=features[2], tf_idf=1, weight=w).save()

        EventFeature(event=events[5], feature=features[3], tf_idf=1, weight=w).save()

        from recommendation import Recommendation
        self.recommendation = Recommendation()

    def test_RFSP(self):
        RR = [[-1,4,-1,-1,5,-1],[-1,3,-1,4,-1,-1],[-1,-1,-1,-1,-1,4],[5,-1,3,-1,-1,-1]]
        FF = [[-1,1,-1,-1],[1,1,-1,-1],[-1,1,1,-1],[-1,1,-1,-1],[1,1,1,-1],[-1,-1,-1,1]]
        SS = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        PP = [[2,2,1,0],[1,2,0,0],[0,0,0,1],[0,2,1,0]]

        self.recommendation.init_basic_matrix()
        if not compare_list(RR, transform_matrix_list(self.recommendation.get_matrix_r())):
            print 'error RR test_RFSP'
            print RR, '\n', transform_matrix_list(self.recommendation.get_matrix_r())
        if not compare_list(FF, transform_matrix_list(self.recommendation.get_matrix_f())):
            print 'error FF test_RFSP'
            print FF, '\n', transform_matrix_list(self.recommendation.get_matrix_f())
        if not compare_list(SS, transform_matrix_list(self.recommendation.get_matrix_s())):
            print 'error SS test_RFSP'
            print SS, '\n', transform_matrix_list(self.recommendation.get_matrix_s())
        if not compare_list(PP, transform_matrix_list(self.recommendation.get_matrix_p())):
            print 'error PP test_RFSP'
            print PP, '\n', transform_matrix_list(self.recommendation.get_matrix_p())

    def test_FF_UF_IUF(self):
        FF = [[2,2,1,0],[1,2,0,0],[0,0,0,1],[0,2,1,0]]
        UF = [2,3,2,1]
        IUF = [0.30102999566398114, 0.1249387366082999, 0.30102999566398114, 0.6020599913279623]

        self.recommendation.init_frequency_matrix()
        if not compare_list(FF, transform_matrix_list(self.recommendation.get_matrix_ff())):
            print 'error FF test_RFSP'
            print FF, '\n', transform_matrix_list(self.recommendation.get_matrix_ff())
        if not compare_list(UF, transform_matrix_list(self.recommendation.get_matrix_uf())):
            print 'error UF test_RFSP'
            print UF, '\n', transform_matrix_list(self.recommendation.get_matrix_uf())
        if not compare_list(IUF, transform_matrix_list(self.recommendation.get_matrix_iuf())):
            print 'error IUF test_RFSP'
            print IUF, '\n', transform_matrix_list(self.recommendation.get_matrix_iuf())

    def test_W_UU(self):
        W = [[0.6020599913279623, 0.2498774732165998, 0.30102999566398114, -1], [0.30102999566398114, 0.2498774732165998, -1, -1], [-1, -1, -1, 0.6020599913279623], [-1, 0.2498774732165998, 0.30102999566398114, -1]]
        UU = [[-1, 0.95551065333456875, -1.0, 1.0], [0.95551065333456875, -1, -1.0, 1], [-1.0, -1.0, -1, -1.0], [1, 1, -1.0, -1]]

        self.recommendation.compute_matrix_w()
        self.recommendation.compute_matrix_uu()
        if not compare_list(W, transform_matrix_list(self.recommendation.get_matrix_w())):
            print 'error W test_RFSP'
            print W, '\n', transform_matrix_list(self.recommendation.get_matrix_w())
        if not compare_list(UU, transform_matrix_list(self.recommendation.get_matrix_uu())):
            print 'error UU test_RFSP'
            print UU, '\n', transform_matrix_list(self.recommendation.get_matrix_uu())

    def test_final(self):
        events = Event.objects.all()
        res = {events[0]: 3, events[2]: 5, events[4] : 6}
        res = OrderedDict(sorted(res.items(), key=lambda t: t[1], reverse=True))

        if not compare_ordered_dict(self.recommendation.compute_recommended_events(User.objects.all()[1]), res):
            print 'error final result'
            print res
            print self.recommendation.compute_recommended_events(User.objects.all()[1])