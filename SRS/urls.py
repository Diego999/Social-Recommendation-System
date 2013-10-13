from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'main.views.index', name='index'),
    url(r'^manage$', 'main.views.manage', name='manage'),
    url(r'^addEvent$', 'events.views.addEvent', name='addEvent'),
    url(r'^fetchDatabase$', 'events.views.fetchDatabase', name='fetchDatabase'),
    url(r'^addEventProcess', 'events.views.addEventProcess', name='addEventProcess'),
)
