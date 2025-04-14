from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='reviews-home'),
    path('tickets/', views.ticket_list, name='ticket-list'),
    path('create_review/', views.create_review, name='create-review'),
]
