from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^books$', views.home),
    url(r'^books/add$', views.add),
    url(r'^addbook$', views.addbook),
    url(r'^books/(?P<book_id>\d+)$', views.show),
    url(r'^delete/(?P<book_id>\d+)/(?P<review_id>\d+)$', views.delete),
    url(r'^addreview/(?P<book_id>\d+)$', views.addreview),
    url(r'^users/(?P<user_id>\d+)$', views.users),
    url(r'^logout$', views.logout),

]
