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
def my_ticket_list(request):
    """
        Affiche la liste des tickets créés ou critiqués par l'utilisateur connecté.

        Args:
            request (HttpRequest): La requête HTTP reçue.

        Returns:
            HttpResponse: La page HTML contenant la liste des tickets.
    """
    tickets = Ticket.objects.filter(Q(user=request.user)|Q(review__user=request.user)).order_by('-time_created')
    return render(request, 'reviews/ticket_list_flux.html', {'tickets': tickets})

@login_required
def flux(request):
    """
        Affiche la liste des tickets de l'utilisateur et de ses abonnements.

        Args:
            request (HttpRequest): La requête HTTP reçue.

        Returns:
            HttpResponse: La page HTML contenant la liste des tickets dans le flux.
    """
    followed_users_ids = (UserFollows.objects.filter(user=request.user,is_blocked=False).values_list
                          ('followed_user_id', flat=True))

    tickets = Ticket.objects.filter(
        Q(user=request.user) | Q(user__in=followed_users_ids)
    ).order_by('-time_created')

    return render(request, 'reviews/ticket_list_flux.html', {'tickets': tickets})


def subscriptions_ticket_list(request):
    """
        Affiche tous les tickets existants (pour tests/débogage).

        Args:
            request (HttpRequest): La requête HTTP reçue.

        Returns:
            HttpResponse: La page HTML contenant tous les tickets.
    """
    tickets = Ticket.objects.all()
    return render(request, 'reviews/ticket_list_flux.html', {'tickets': tickets})


@login_required
def create_ticket(request):
    """
        Crée un nouveau ticket, avec optionnellement une critique associée.

        Si la méthode est POST, traite et sauvegarde le ticket et la critique (si présente),
        puis redirige vers le flux.

        Args:
            request (HttpRequest): La requête HTTP reçue.

        Returns:
            HttpResponse: La page de création de ticket (GET) ou redirection après création (POST).
    """
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

            return redirect('flux')
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()

    return render(request, 'reviews/create_ticket.html', {
        'ticket_form': ticket_form,
        'review_form': review_form,
    })


@login_required
def edit_ticket(request, ticket_id):
    """
       Permet à l'utilisateur connecté de modifier un de ses tickets.

       Args:
           request (HttpRequest): La requête HTTP reçue.
           ticket_id (int): ID du ticket à modifier.

       Returns:
           HttpResponse: La page d'édition du ticket (GET) ou redirection après modification (POST).
    """
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES, instance=ticket)
        if ticket_form.is_valid():
            ticket_form.save()
            return redirect('flux')  # Redirection après modification
    else:
        ticket_form = TicketForm(instance=ticket)

    return render(request, 'reviews/edit_ticket.html', {
        'ticket_form': ticket_form,
        'ticket': ticket
    })


@login_required
def delete_ticket(request, ticket_id):
    """
        Permet à l'utilisateur connecté de supprimer un de ses tickets.

        Args:
            request (HttpRequest): La requête HTTP reçue.
            ticket_id (int): ID du ticket à supprimer.

        Returns:
            HttpResponse: La page de confirmation ou redirection après suppression.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == 'POST':
        ticket.delete()
        return redirect('flux')  # ou 'posts', selon le contexte

    return render(request, 'reviews/delete_ticket.html', {
        'ticket': ticket
    })

@login_required
def edit_review(request, review_id):
    """
       Permet à l'utilisateur connecté de modifier une de ses critiques.

       Args:
           request (HttpRequest): La requête HTTP reçue.
           review_id (int): ID de la critique à modifier.

       Returns:
           HttpResponse: La page d'édition ou redirection après modification.
    """
    # Récupérer la review avec l'ID, et la lier à l'utilisateur connecté
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        review_form = ReviewForm(request.POST, instance=review)  # Pré-remplir la review

        if review_form.is_valid():
            review_form.save()  # Sauvegarder la review mise à jour
            return redirect('flux')  # Redirection après modification
    else:
        review_form = ReviewForm(instance=review)

    return render(request, 'reviews/edit_review.html', {
        'review_form': review_form,
        'review': review
    })


@login_required
@csrf_exempt
def create_review_for_ticket(request, ticket_id):
    """
       Crée une critique pour un ticket donné (via AJAX ou formulaire classique).

       Args:
           request (HttpRequest): La requête HTTP reçue.
           ticket_id (int): ID du ticket à critiquer.

       Returns:
           JsonResponse ou HttpResponse: Réponse JSON si AJAX, ou redirection/page HTML sinon.
    """
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

            return redirect('flux')

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
    """
        Gère les abonnements et le blocage d'utilisateurs.

        Permet de :
        - S'abonner à un utilisateur par son nom.
        - Se désabonner.
        - Bloquer/débloquer un utilisateur.

        Args:
            request (HttpRequest): La requête HTTP reçue.

        Returns:
            HttpResponse: La page des abonnements.
    """
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
    """
        Permet à l'utilisateur connecté de supprimer une de ses critiques.

        Args:
            request (HttpRequest): La requête HTTP reçue.
            review_id (int): ID de la critique à supprimer.

        Returns:
            HttpResponse: La page de confirmation ou redirection après suppression.
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        review.delete()
        return redirect('flux')  # ou 'posts', selon le contexte

    return render(request, 'reviews/delete_review.html', {
        'review': review
    })


def create_ticket_only(request):
    """
        Crée uniquement un ticket, sans critique associée.

        Args:
            request (HttpRequest): La requête HTTP reçue.

        Returns:
            HttpResponse: La page de création du ticket ou redirection après création.
    """
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
    """
       Permet à un nouvel utilisateur de créer un compte.

       Args:
           request (HttpRequest): La requête HTTP reçue.

       Returns:
           HttpResponse: La page d'inscription ou redirection vers la page de connexion après inscription.
    """
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
