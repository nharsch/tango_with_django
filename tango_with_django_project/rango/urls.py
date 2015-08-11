from django.conf.urls import patterns, url
from rango import views

urlpatterns = patterns('', 
                       url(r'^$', views.index, name='index'),
                       url(r'^about/', views.about, name='about'),
                       url(r'^add_category/$', views.add_category, name='add_category'), 
                       url(r'^auto_add_page/$', views.auto_add_page, name='auto_add_page'),
                       url(r'^upload/$', views.upload, name='upload'),
                       url(r'^upload_verify/$', views.upload_verify, name='upload_verify'),
                       # url(r'^add_pages/$', views.add_pages, name="add_pages"),
                       url(r'^manifest_add/$', views.manifest_add, name='manifest_add'),
                       url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
                       url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
                       url(r'^like_category/$', views.like_category, name='like_category'),
                       url(r'search', views.search, name='search'),
                       url(r'suggest_category/$', views.suggest_category, name='suggest_category'),
                       url(r'goto', views.track_url, name='goto'),
                       url(r'add_profile', views.register_profile, name='add_profile'),
                       url(r'users', views.list_users, name="list_users"),
                       url(r'^restricted/', views.restricted, name='restricted'),
                       )
