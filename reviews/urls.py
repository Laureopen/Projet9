from django.urls import path
from . import views

urlpatterns = [
    path('créer-une-critique/', views.create_ticket, name='create_ticket'),
    path('creer-un-ticket/', views.create_ticket_only, name='create_ticket_only'),
    path('ticket/<int:ticket_id>/create-review/', views.create_review_for_ticket, name='create-review-for-ticket'),
    path('ticket/<int:ticket_id>/ask_review/', views.ask_review, name='ask_review'),
    path('ticket/<int:ticket_id>/edit/', views.edit_ticket, name='edit_ticket'),
    path('ticket/<int:ticket_id>/delete/', views.delete_ticket, name='delete_ticket'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('flux/', views.flux, name='flux'),
    path('posts/', views.my_ticket_list, name='posts'),
    path('abonnements/', views.subscriptions, name='abonnements'),
    path('register/', views.register, name='register')
]
