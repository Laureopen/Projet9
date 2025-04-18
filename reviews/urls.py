from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='reviews-home'),
    path('tickets/', views.ticket_list, name='ticket-list'),
    path('flux/', views.flux, name='flux'),
    path('posts/', views.posts_view, name='posts'),
    path('abonnements/', views.abonnements, name='abonnements'),
    path('demander-critique/', views.ask_review, name='ask_review'),
    path('créer-une-critique/', views.create_review, name='create_review'),
    path('modifier/', views.ask_review, name='modify_post'),
    path('supprimer/', views.create_review, name='delete_post'),



]
