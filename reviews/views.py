from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import TicketForm, ReviewForm, PostForm
from .models import Ticket, Review, Post, UserFollows
from django.contrib.auth.decorators import login_required
from django.db.models import Q


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


@login_required
def flux(request):
    # Récupérer les IDs des utilisateurs suivis
    followed_users_ids = UserFollows.objects.filter(user=request.user).values_list('followed_user_id', flat=True)

    # Tickets de moi + des gens que je suis
    tickets = Ticket.objects.filter(
        Q(user=request.user) | Q(user__in=followed_users_ids)
    ).order_by('-time_created')

    return render(request, 'reviews/ticket_list.html', {'tickets': tickets})


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


@login_required
def subscriptions(request):
    message = ""

    if request.method == 'POST':
        if 'unfollow_id' in request.POST:
            user_id = request.POST.get('unfollow_id')
            to_unfollow = get_object_or_404(User, id=user_id)
            UserFollows.objects.filter(user=request.user, followed_user=to_unfollow).delete()
            message = f"Vous vous êtes désabonné de {to_unfollow.username}."
        else:
            username = request.POST.get('username')
            try:
                to_follow = User.objects.get(username=username)
                if to_follow == request.user:
                    message = "Vous ne pouvez pas vous abonner à vous-même."
                elif UserFollows.objects.filter(user=request.user, followed_user=to_follow).exists():
                    message = "Vous êtes déjà abonné à cet utilisateur."
                else:
                    UserFollows.objects.create(user=request.user, followed_user=to_follow)
                    message = f"Abonnement à {to_follow.username} réussi."
            except User.DoesNotExist:
                message = "Utilisateur non trouvé."

    abonnements = request.user.following.select_related('followed_user')
    abonnés = request.user.followers.select_related('user')

    return render(request, 'reviews/subscriptions.html', {
        'abonnements': abonnements,
        'abonnes': abonnés,
        'message': message,
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


@login_required
def my_ticket_list(request):
    tickets = Ticket.objects.filter(user=request.user).order_by('-time_created')
    return render(request, 'reviews/ticket_list.html', {'tickets': tickets})