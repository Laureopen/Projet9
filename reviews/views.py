from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import TicketForm, ReviewForm
from .models import Ticket

def home(request):
    return HttpResponse("Bienvenue dans l'application Reviews ! 🎉")


def ticket_list(request):
    tickets = Ticket.objects.all()
    return render(request, 'reviews/ticket_list.html', {'tickets': tickets})


def create_review(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect('ticket-list')  # redirection après création
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()

    return render(request, 'reviews/create_review.html', {
        'ticket_form': ticket_form,
        'review_form': review_form,
    })
