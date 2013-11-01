from event_analyse.tree_tagger import TreeTagger

FACEBOOK_APP_ID = '243857849099325'
FACEBOOK_SECRET_KEY = '1e209962c6eadb448a5396e72bfca57b'
FACEBOOK_REDIRECT_URL = 'http://localhost:8000/facebook_login_success'

FRENCH_STOPWORDS_FILE = 'data/stopwords/frenchST.txt'

K_MOST_IMPORTANT_KEYWORD = 10
WEIGHT_DESCRIPTION_TEXT = 1.0
WEIGHT_WEBSITE_TEXT = 0.5

FILTER_TREE_TAGGER = [TreeTagger.noun]
FILTER_TAGS_WEBSITE = ['p']