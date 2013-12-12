from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'main.views.index', name='index'),
    url(r'^manage/$', 'main.views.manage', name='manage'),
    url(r'^add_event/$', 'events.views.add_event', name='add_event'),
    url(r'^fetch_database/$', 'events.views.fetch_database', name='fetch_database'),
    url(r'^add_event_process/$', 'events.views.add_event_process', name='add_event_process'),
    url(r'^display_event_added/$', 'events.views.display_event_added', name='display_event_added'),
    url(r'^list_events/$', 'events.views.list_events', name='list_events'),
    url(r'^facebook_login/$', 'FBGraph.views.facebook_login', name='facebook_login'),
    url(r'^facebook_login_success/$', 'FBGraph.views.facebook_login_success', name='facebook_login_success'),
    url(r'^facebook_info/$', 'FBGraph.views.facebook_info', name='facebook_info'),
    url(r'^facebook_analysis/$', 'FBGraph.views.facebook_analysis', name='facebook_analysis'),
    url(r'^list_event_feature/$', 'event_analyse.views.list_event_features', name='list_event_features'),
    url(r'^event_analysis/$', 'event_analyse.views.event_analysis', name='event_analysis'),
    url(r'^recommendation/$', 'recommendation.views.view_recommendation', name='view_recommendation'),
    url(r'^rate_event/(?P<external_id>\d+)/(?P<rating>[-]?\w+)', 'events.views.rate_event', name='rate_event')
)
