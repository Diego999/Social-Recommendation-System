import guess_language
import threading
from job_queue import JobQueue
from multiprocessing import cpu_count
from app_config import *
from html_parser_by_tag import HTMLParserByTag
from event_analysis import EventAnalysis
from events.models import Event, Feature, EventFeature
from tree_tagger import TreeTagger
from website_link_arborescence import *


def is_nb_word_website_enough(x):
    return x


def event_analysis():
    """
    Event analysis process. It fetches all the event in the database and analyse the description & website and
    then create all the related features
    """
    event_analysis = EventAnalysis()

    # Store all available website and avoid parsing a website several times
    websites = dict(dict())

    #  Contains the list of key-word with tree tagger
    description_tree_tagger = dict()
    website_tree_tagger = dict()

    nb_core = cpu_count()

    events = Event.objects.all()[:20]

    if len(events) == 0:
        return

    nb_events = len(events)
    nb_events_thread = nb_events/nb_core
    events_thread = []

    for i in range(nb_core-1):
        events_thread.append(events[i*nb_events_thread:(i+1)*nb_events_thread])
    events_thread.append(events[(nb_core-1)*nb_events_thread:])

    # Fulfill the corpus
    start_threads(nb_core, event_analysis_fulfill_corpus,
                  events_thread, event_analysis, websites, description_tree_tagger, website_tree_tagger)

    event_analysis.set_corpus_complete()

    # We compute the tf-idf of the key word in the description and in the website if exists
    start_threads(nb_core, event_analysis_compute_tf_idf,
                  events_thread, event_analysis, websites, description_tree_tagger, website_tree_tagger)

    # We fetch the k most important tags by event
    job_queue = JobQueue()
    job_queue.start()
    start_threads(nb_core, event_analysis_fetch_k_most_important_features_and_push_database,
                  events_thread, job_queue, event_analysis, websites)
    job_queue.finish()


def start_threads(nb_core, fct, tab, *args):
    threads = []
    for i in range(nb_core):
        thread = threading.Thread(target=fct, args=args + (tab[i],))
        threads.append(thread)
        thread.start()

    for t in threads:
        t.join()

def event_analysis_fulfill_corpus(event_analysis, websites, description_tree_tagger, website_tree_tagger, events):
    """
    Part 1 of the event analysis, that fulfill the corpus
    """
    tagger = TreeTagger()

    # We complete the corpus with plain text of description & website if exists
    for e in events:
        if e.description != '' and guess_language.guessLanguage(e.description.encode('utf-8')) == LANGUAGE_FOR_TEXT_ANALYSIS:
            event_analysis.add_document_in_corpus(e.description, EventAnalysis.get_id_website(e.id, False))
            description_tree_tagger[EventAnalysis.get_id_website(e.id, False)] = tagger.tag_text(e.description,
                                                                                                 FILTER_TREE_TAGGER)

        if e.website != '':
            try:
                unique_urls = HashTableUrl()
                TreeNode(e.website.encode('utf-8'), DEFAULT_RECURSION_WEBSITE, unique_urls)
                websites[e.website] = dict([(w, event_website_analyse(w)) for w in unique_urls.get_urls()])
                website_tree_tagger[EventAnalysis.get_id_website(e.id, True)] = list()
                for k, v in websites[e.website].items():
                    event_analysis.add_document_in_corpus(v, EventAnalysis.get_id_website(e.id, True))
                    website_tree_tagger[EventAnalysis.get_id_website(e.id, True)] += tagger.tag_text(v,
                                                                                                     FILTER_TREE_TAGGER)
                    nb_key_word = len(website_tree_tagger[EventAnalysis.get_id_website(e.id, True)])
                    if nb_key_word >= is_nb_word_website_enough(nb_key_word):
                        break

            # Some website :
            # - has a 403 error, eg: complexe3d.com,
            # - is nonexistent website like http://www.biblio.morges.ch
            # - is not a web url ... like galerie@edouardroch.ch,
            # thhp://www.vitromusee.ch (the typo is on purpose !), www,chateaudeprangins.ch, http://
            except (HTTPError, URLError, ValueError) as e:  # We must know the other kind of error as conversion problem
                pass


def event_analysis_compute_tf_idf(event_analysis, websites, description_tree_tagger, website_tree_tagger, events):
    """
    Part 2 of event analysis that compute the tf_idf of each feature in the related document
    """
    for e in events:
        if e.description != '' and EventAnalysis.get_id_website(e.id, False) in description_tree_tagger.keys():
            for k in description_tree_tagger[EventAnalysis.get_id_website(e.id, False)]:
                event_analysis.compute_tf_idf(k, EventAnalysis.get_id_website(e.id, False))

        if e.website in websites.keys() and EventAnalysis.get_id_website(e.id, True) in website_tree_tagger.keys():
            for k in website_tree_tagger[EventAnalysis.get_id_website(e.id, True)]:
                event_analysis.compute_tf_idf(k, EventAnalysis.get_id_website(e.id, True))


def event_analysis_fetch_k_most_important_features_and_push_database(job_queue, event_analysis, websites, events):
    """
    Part 3 of event analysis that fetch the k most important features for an event and push them into the database
    """
    from collections import OrderedDict
    from itertools import islice

    for e in events:
        key_words_description = OrderedDict()
        if e.description != '':
            key_words_description = event_analysis.get_tf_idf_the_k_most_important(K_MOST_IMPORTANT_KEYWORD,
                                                                            EventAnalysis.get_id_website(e.id, False))

        key_words_website = OrderedDict()
        if e.website in websites.keys():
            key_words_website = event_analysis.get_tf_idf_the_k_most_important(K_MOST_IMPORTANT_KEYWORD,
                                                                               EventAnalysis.get_id_website(e.id, True))

        key_words_description_keys = key_words_description.keys()
        key_words_website_keys = key_words_website.keys()

        # Input => 2 merges orderedDict as (tag, (frequency, idf))
        # Output key_words -> OrderedDict(tag, idf), len = K_MOST_IMPORTANT_KEYWORD
        # Mix key words in description and website to keep the most k important terms.
        # If there is a key in the both dict, we compute the average (frequency + idf)
        # and we MUST resort (we use the frequency) the dictionary to keep only the most k important
        key_words = OrderedDict(
            (x[0], x[1][1]) for x in(islice(OrderedDict(sorted(
                    dict({(k
                        ,  # Average frequency
                      ((key_words_description.get(k)[0] if k in key_words_description_keys else 0.0 + key_words_website.get(k)[0] if k in key_words_website_keys else 0.0)
                       /(2.0 if k in key_words_description_keys and k in key_words_website_keys else 1.0)
                       ,  # Average idf
                       (key_words_description.get(k)[1] if k in key_words_description_keys else 0.0 + key_words_website.get(k)[1] if k in key_words_website_keys else 0.0)
                       /(2.0 if k in key_words_description_keys and k in key_words_website_keys else 1.0))
                     )
                     #  Finally, we sort inversely the dict by the frequency and we keep the K_MOST_IMPORTANT_KEY values
                     for k in (key_words_description_keys + key_words_website_keys)}).iteritems(), key=lambda x: x[1][0], reverse=True)).items(), 0, K_MOST_IMPORTANT_KEYWORD)))

        # Django ORM database is not thread safe, so we have to use a job queue
        job_queue.put([update_database_event_tags, e, key_words])


def event_website_analyse(url):
    """
    Parsed the website of an event
    """
    if url == '':
        raise Exception("The event doesn't have any website")

    parser = HTMLParserByTag()
    html = parser.unescape(urllib2.urlopen(url.encode('utf-8')).read().decode('utf-8'))
    parsed_text = ''

    for t in FILTER_TAGS_WEBSITE:
        parser.initialize(t)
        parser.feed(html)
        parsed_text += parser.get_data() + ' '

    return parsed_text if guess_language.guessLanguage(parsed_text.encode('utf-8')) == LANGUAGE_FOR_TEXT_ANALYSIS else''


def update_database_event_tags(event, key_words):
    """
    Update all the necessary information for a event-features
    """
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
    """
    Return the list of all events with related features
    """
    events = Event.objects.all()

    out = dict()
    for e in events:
        out[e] = [(ef.feature.name, ef.tf_idf) for ef in EventFeature.objects.filter(event__exact=e)]

    return out

