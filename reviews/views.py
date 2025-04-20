from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import TicketForm, ReviewForm, PostForm
from .models import Ticket, Review, Post, UserFollows
from django.shortcuts import get_object_or_404


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


def posts_view(request):
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'reviews/posts.html', {'posts': posts})


def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('posts')  # redirige vers la page qui affiche les posts
    else:
        form = PostForm()
    return render(request, 'reviews/create_post.html', {'form': form})


def abonnements(request):
    if request.method == 'POST':
        username_to_follow = request.POST.get('username')
        try:
            user_to_follow = User.objects.get(username=username_to_follow)
            if user_to_follow != request.user:
                UserFollows.objects.get_or_create(user=request.user, followed_user=user_to_follow)
        except User.DoesNotExist:
            pass  # ou gérer une erreur utilisateur non trouvé

        return redirect('abonnements')  # recharge la page après l’ajout

    abonnements = UserFollows.objects.filter(user=request.user)
    abonnes = UserFollows.objects.filter(followed_user=request.user)

    return render(request, 'reviews/abonnements.html', {
        'abonnements': abonnements,
        'abonnes': abonnes,
    })

def ask_review(request):
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

    return render(request, 'reviews/ask_review.html', {
        'ticket_form': ticket_form,
        'review_form': review_form,
    })


def create_ticket(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('ticket-list')
    else:
        ticket_form = TicketForm()  # pour les requêtes GET

    return render(request, 'reviews/create_ticket.html', {
        'ticket_form': ticket_form
    })


def ticket_list(request):
    tickets = Ticket.objects.all()
    return render(request, 'reviews/ticket_list.html', {'tickets': tickets})


def create_review_for_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect('ticket-list')  # Redirection après création de la review
    else:
        review_form = ReviewForm()

    return render(request, 'reviews/create_review.html', {
        'review_form': review_form,
        'ticket': ticket,
    })