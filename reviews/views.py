from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from .forms import TicketForm, ReviewForm
from .models import Ticket, UserFollows, Review


@login_required
def ask_review(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    ticket.asked_review = True
    ticket.save()
    return redirect('posts')


def ticket_list(request):
    tickets = Ticket.objects.all().order_by('-time_created')
    return render(request, 'reviews/ticket_list_flux.html', {'tickets': tickets})


@login_required
def my_ticket_list(request):
    tickets_created = Ticket.objects.filter(user=request.user)
    tickets_reviewed = Ticket.objects.filter(review__user=request.user)
    tickets = (tickets_created | tickets_reviewed).distinct().order_by('-time_created')
    return render(request, 'reviews/ticket_list_flux.html', {'tickets': tickets})


@login_required
def flux(request):
    # Récupérer les IDs des utilisateurs suivis
    followed_users_ids = (UserFollows.objects.filter(user=request.user, is_blocked=False).values_list
                          ('followed_user_id', flat=True))

    # Tickets de moi + des gens que je suis
    tickets = Ticket.objects.filter(
        Q(user=request.user) | Q(user__in=followed_users_ids)
    ).order_by('-time_created')

    return render(request, 'reviews/ticket_list_flux.html', {'tickets': tickets})


def subscriptions_ticket_list(request):
    tickets = Ticket.objects.all()
    return render(request, 'reviews/ticket_list_flux.html', {'tickets': tickets})


@login_required
def create_ticket(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)

        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            if review_form.is_valid() and review_form.cleaned_data.get('headline'):  # S'il y a une review remplie
                review = review_form.save(commit=False)
                review.ticket = ticket
                review.user = request.user
                review.save()

            return redirect('ticket-list')
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()

    return render(request, 'reviews/create_ticket.html', {
        'ticket_form': ticket_form,
        'review_form': review_form,
    })


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES, instance=ticket)
        if ticket_form.is_valid():
            ticket_form.save()
            return redirect('ticket-list')  # Redirection après modification
    else:
        ticket_form = TicketForm(instance=ticket)

    return render(request, 'reviews/edit_ticket.html', {
        'ticket_form': ticket_form,
        'ticket': ticket
    })


@login_required
def delete_ticket(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        review.delete()
        return redirect('ticket-list')  # ou 'posts', selon le contexte

    return render(request, 'reviews/delete_ticket.html', {
        'review': review
    })


@login_required
def edit_review(request, review_id):
    # Récupérer la review avec l'ID, et la lier à l'utilisateur connecté
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        review_form = ReviewForm(request.POST, instance=review)  # Pré-remplir la review

        if review_form.is_valid():
            review_form.save()  # Sauvegarder la review mise à jour
            return redirect('ticket-list')  # Redirection après modification
    else:
        review_form = ReviewForm(instance=review)

    return render(request, 'reviews/edit_review.html', {
        'review_form': review_form,
        'review': review
    })


@login_required
@csrf_exempt
def create_review_for_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('reviews/single_review.html', {'review': review})
                return JsonResponse({'html': html})

            return redirect('ticket-list')

    else:
        review_form = ReviewForm()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('reviews/review_form_partial.html', {
            'review_form': review_form,
            'ticket': ticket,
        })
        return JsonResponse({'html': html})

    return render(request, 'reviews/create_review.html', {
        'review_form': review_form,
        'ticket': ticket,
    })


@login_required
def subscriptions(request):
    if request.method == 'POST':
        if 'unfollow_id' in request.POST:
            user_id = request.POST.get('unfollow_id')
            to_unfollow = get_object_or_404(User, id=user_id)
            UserFollows.objects.filter(user=request.user, followed_user=to_unfollow).delete()
            messages.success(request, f"Vous vous êtes désabonné de {to_unfollow.username}.")

        elif 'toggle_block_id' in request.POST:
            user_id = request.POST.get('toggle_block_id')
            try:
                user_to_toggle = User.objects.get(id=user_id)

                if user_to_toggle == request.user:
                    messages.error(request, "Vous ne pouvez pas vous bloquer vous-même.")
                else:
                    follow = UserFollows.objects.get(user=user_to_toggle, followed_user=request.user)
                    follow.is_blocked = not follow.is_blocked
                    follow.save()
                    action = "bloqué" if follow.is_blocked else "débloqué"
                    messages.success(request, f"Utilisateur {user_to_toggle.username} {action} avec succès.")

            except User.DoesNotExist:
                messages.error(request, "Utilisateur introuvable.")
            except UserFollows.DoesNotExist:
                messages.error(request, "Relation de suivi introuvable pour effectuer le blocage.")

        else:
            username = request.POST.get('username')
            try:
                to_follow = User.objects.get(username=username)
                if to_follow == request.user:
                    messages.error(request, "Vous ne pouvez pas vous abonner à vous-même.")
                elif UserFollows.objects.filter(user=request.user, followed_user=to_follow).exists():
                    messages.warning(request, "Vous êtes déjà abonné à cet utilisateur.")
                else:
                    UserFollows.objects.create(user=request.user, followed_user=to_follow)
                    messages.success(request, f"Abonnement à {to_follow.username} réussi.")
            except User.DoesNotExist:
                messages.error(request, "Utilisateur non trouvé.")

    abonnements = request.user.following.select_related('followed_user')
    abonnes = request.user.followers.select_related('user')

    return render(request, 'reviews/subscriptions.html', {
        'abonnements': abonnements,
        'abonnes': abonnes,
    })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        review.delete()
        return redirect('ticket-list')  # ou 'posts', selon le contexte

    return render(request, 'reviews/delete_review.html', {
        'review': review
    })


def create_ticket_only(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('posts')  # redirection après création
    else:
        ticket_form = TicketForm()
    return render(request, 'reviews/create_ticket_only.html', {
        'ticket_form': ticket_form
    })


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']

        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return render(request, 'register.html')

        user = User.objects.create_user(username=username, password=password)
        user.save()
        return redirect('login')  # Redirige vers la page de login après inscription

    return render(request, 'register.html')
