from django.shortcuts import render
from django.http import HttpResponse
from .models import Ticket

def home(request):
    return HttpResponse("Bienvenue dans l'application Reviews ! 🎉")

def ticket_list(request):
    tickets = Ticket.objects.all()
    return render(request, 'reviews/ticket_list.html', {'tickets': tickets})

