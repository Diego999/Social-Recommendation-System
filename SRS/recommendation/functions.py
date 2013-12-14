from recommendation import Recommendation


def compute_recommendation():
    recommendation = Recommendation()
    recommendation.init_basic_matrix()
    recommendation.init_frequency_matrix()
    recommendation.compute_matrix_w()
    print recommendation.get_matrix_w()