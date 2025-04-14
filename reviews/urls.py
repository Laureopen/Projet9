from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='reviews-home'),
    path('tickets/', views.ticket_list, name='ticket-list')

]
