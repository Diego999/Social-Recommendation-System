import urllib2
from urllib2 import HTTPError, URLError
from app_config import *
from html_parser_by_tag import HTMLParserByTag
from event_analysis import Event_analysis
from events.models import Event, Feature, EventFeature
from tree_tagger import TreeTagger

def event_analysis():
    events = Event.objects.all()

    event_analysis = Event_analysis()

    websites = dict() # Store all available website and avoid parsing a website several times

    # We complete the corpus with plain text of description & website if exists
    for e in events:
        if e.description != '':
            event_analysis.add_document_in_corpus(e.description, e.id, False)
        if e.website != '':
            try:
                websites[e.website] = event_website_analyse(e)
                event_analysis.add_document_in_corpus(websites[e.website], e.id, True)
            # Some website :
            # - has a 403 error, eg: complexe3d.com,
            # - is inexistant website like http://www.biblio.morges.ch
            # - is not a web url ... like galerie@edouardroch.ch, thhp://www.vitromusee.ch (the typo is on purpose !), www,chateaudeprangins.ch, http://
            except (HTTPError, URLError, ValueError) as e:
                pass

    event_analysis.set_corpus_complete()

    # We compute the tf-idf of the key word in the description and in the website if exists
    tagger = TreeTagger()
    for e in events:
        if e.description != '':
            for k in tagger.tag_text(e.description, FILTER_TREE_TAGGER):
                event_analysis.compute_tf_idf(k, e.id, False)
        if e.website in websites.keys():
            for k in tagger.tag_text(websites[e.website], FILTER_TREE_TAGGER):
                event_analysis.compute_tf_idf(k, e.id, True)


    from collections import OrderedDict
    from itertools import islice

    # We fetch the k most important tags by event
    for e in events:
        key_words_description = OrderedDict()
        if e.description != '':
            key_words_description = event_analysis.get_tf_idf_the_k_most_important(K_MOST_IMPORTANT_KEYWORD, e.id, False)

        key_words_website = OrderedDict()
        if e.website in websites.keys():
            key_words_website = event_analysis.get_tf_idf_the_k_most_important(K_MOST_IMPORTANT_KEYWORD, e.id, True)

        key_words_description_keys = key_words_description.keys()
        key_words_website_keys = key_words_website.keys()

        # Input => 2 merges orderedDict as (tag, (frequency, idf))
        # Output key_words -> OrderdDict(tag, idf), len = K_MOST_IMPORTANT_KEYWORD
        # Mix key words in description and website to keep the most k important terms.
        # If there is a key in the both dict, we compute the average (frequency + idf)
        # and we MUST resort (we use the frequency) the dictionary to keep only the most k important
        key_words = OrderedDict(
            (x[0], x[1][1]) for x in(islice(OrderedDict(sorted(
                    dict({(k,
                      ((key_words_description.get(k)[0] if k in key_words_description_keys else 0.0 + key_words_website.get(k)[0] if k in key_words_website_keys else 0.0)
                       /(2.0 if k in key_words_description_keys and k in key_words_website_keys else 1.0)
                       ,
                       (key_words_description.get(k)[1] if k in key_words_description_keys else 0.0 + key_words_website.get(k)[1] if k in key_words_website_keys else 0.0)
                       /(2.0 if k in key_words_description_keys and k in key_words_website_keys else 1.0))
                     )
                     for k in (key_words_description_keys + key_words_website_keys)}).iteritems(), key=lambda x: x[1][0], reverse=True)).items(), 0, K_MOST_IMPORTANT_KEYWORD)))

        update_database_event_tags(e, key_words)


def event_website_analyse(event):
    if event.website == '':
        raise Exception("The event doesn't have any website")

    parser = HTMLParserByTag()
    html = parser.unescape(urllib2.urlopen(event.website.encode('utf8')).read().decode('ascii', 'ignore'))
    parsed_text = ''

    for t in FILTER_TAGS_WEBSITE:
        parser.initialize(t)
        parser.feed(html)
        parsed_text += parser.get_data()

    return parsed_text

def update_database_event_tags(event, key_words):
    features = Feature.objects.all()
    feature_names = [f.name for f in features]

    for fe in EventFeature.objects.filter(event=event):
        fe.delete()

    epsilon = 10**-10
    for k, v in key_words.items():
        if v >= epsilon:
            # We insert the new feature or fetch it
            feature = Feature.objects.get(name__exact=k) if k in feature_names else Feature(name=k)
            feature.save()

            EventFeature(event=event, feature=feature, tf_idf=v).save()

def get_list_event_features():
    events = Event.objects.all()

    out = dict()
    for e in events:
        out[e] = [(ef.feature.name, ef.tf_idf) for ef in EventFeature.objects.filter(event__exact=e)]

    return out

