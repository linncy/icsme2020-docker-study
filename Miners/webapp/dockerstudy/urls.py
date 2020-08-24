from django.conf.urls import url
from django.urls import path
from django.urls import include

from . import views

app_name = 'dockerstudy'

urlpatterns = [
    url(r"^image/$", views.request_image, name='post_image'),
    url(r"^create_image/$", views.create_image, name='create_image'),
    url(r"^dockerhub_user/$", views.request_dockerhub_user, name='dockerhub_user'),
    url(r"^image_name_crawler_task/$", views.request_image_name_crawler, name='image_name_crawler_task'),
    url(r"^authtoken/github$", views.request_github_authtoken, name='request_github_authtoken'),
    url(r"^authtoken/bitbucket$", views.request_bitbucket_authtoken, name='request_bitbucket_authtoken'),
    url(r"^authtoken/$", views.request_update_authtoken, name='request_update_authtoken'),
    url(r"^image_and_repo_info_crawler_task/$", views.request_image_and_repo_info_crawler, name='image_and_repo_info_crawler_task'),
    url(r"^repository/$", views.request_repository, name='request_repository'),
    path('query_repository/<str:repo_location>/<str:repo_owner>/<str:repo_name>/', views.query_repository)

]
