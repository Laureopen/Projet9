from django.urls import path
from . import views

urlpatterns = [
    path('creer-un-ticket/', views.create_ticket, name='create_ticket'),
    path('flux/', views.flux, name='flux'),
    path('posts/', views.my_ticket_list, name='posts'),
    path('abonnements/', views.subscriptions, name='abonnements'),
    path('demander-critique/', views.ask_review, name='ask_review'),
    path('modifier/', views.ask_review, name='modify_post'),
    path('tickets/', views.ticket_list, name='ticket-list'),
    path('ticket/<int:ticket_id>/create-review/', views.create_review_for_ticket, name='create-review-for-ticket'),


]
