from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Value, CharField
from django.contrib.auth.decorators import login_required
from .forms import TicketForm, ReviewForm
from .models import Ticket, Review
from itertools import chain

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


def flux(request):
    reviews = Review.objects.select_related("ticket", "user")
    tickets = Ticket.objects.exclude(review__isnull=False)  # tickets sans review associée

    posts = []

    for review in reviews:
        posts.append({
            "header": "Vous avez publié une critique" if review.user == request.user else f"{review.user.username} posted a review",
            "title": review.headline,
            "description": review.body,
            "ticket": review.ticket,
            "timestamp": review.created_at,
            "can_review": False
        })

    for ticket in tickets:
        posts.append({
            "header": f"{ticket.user.username} a demandé une critique",
            "title": ticket.title,
            "description": ticket.description,
            "ticket": ticket,
            "timestamp": ticket.created_at,
            "can_review": True
        })

    posts.sort(key=lambda x: x["timestamp"], reverse=True)

    return render(request, "reviews/flux.html", {"posts": posts})
