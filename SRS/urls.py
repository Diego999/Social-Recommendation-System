from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'main.views.index', name='index'),
    url(r'^manage/$', 'main.views.manage', name='manage'),
    url(r'^add_event/$', 'events.views.add_event', name='add_event'),
    url(r'^fetch_database/$', 'events.views.fetch_database', name='fetch_database'),
    url(r'^add_event_process/$', 'events.views.add_event_process', name='add_event_process'),
    url(r'^display_event_added/$', 'events.views.display_event_added', name='display_event_added'),
    url(r'^facebook_login/$', 'FBGraph.views.facebook_login', name='facebook_login'),
    url(r'^facebook_login_success/$', 'FBGraph.views.facebook_login_success', name='facebook_login_success'),
    url(r'^facebook_info/$', 'FBGraph.views.facebook_info', name='facebook_info')
)
