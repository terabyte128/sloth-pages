__author__ = 'Sam'

from django.conf.urls import patterns, url

from transfusion import views

urlpatterns = patterns(
    '',

    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^t/(?P<teacher>[^/]+)/$', views.teacher_profile, name='teacher_profile'),
    url(r'^t/(?P<teacher>[^/]+)/c/(?P<course>[0-9]+)/$', views.course, name='course'),
    url(r'^sign_in/$', views.sign_in, name="sign_in"),
    url(r'^sign_out/$', views.sign_out, name="sign_out"),

    url(r'^edit_profile/$', views.edit_profile, name='edit_profile'),
    url(r'^edit_course/(?P<course_id>[0-9]+)/$', views.edit_course, name='edit_course'),
    url(r'^edit_course/(?P<course_id>[0-9]+)/add_assignment/$', views.add_assignment, name='add_assignment'),
    url(r'^edit_course/(?P<course_id>[0-9]+)/edit_assignment/(?P<assignment_id>[0-9]+)/$', views.edit_assignment, name='edit_assignment'),
    url(r'^edit_course/(?P<course_id>[0-9]+)/delete_assignment/(?P<assignment_id>[0-9]+)/$', views.delete_assignment, name='delete_assignment'),

    url(r'^edit_course/(?P<course_id>[0-9]+)/info/$', views.edit_course_info, name='edit_course_info'),

    )
