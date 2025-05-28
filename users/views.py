from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    """
        Vue personnalisée pour la connexion des utilisateurs.

        Utilise le template 'users/login.html' pour afficher le formulaire
        de connexion. Hérite de django.contrib.auth.views.LoginView.
    """
    template_name = 'users/login.html'


class CustomLogoutView(LogoutView):
    """
        Vue personnalisée pour la déconnexion des utilisateurs.

        Après déconnexion, redirige vers la page de connexion grâce à
        la propriété next_page qui utilise reverse_lazy('login').
    """
    next_page = reverse_lazy('login')


class RegisterView(CreateView):
    """
       Vue pour l'enregistrement des nouveaux utilisateurs.

       Utilise le formulaire UserCreationForm fourni par Django pour
       gérer la création d'un nouvel utilisateur. Utilise le template
       'users/register.html'. En cas de succès, redirige vers la page
       de connexion.

       Attributs :
           form_class : Formulaire utilisé pour la création d'utilisateur.
           template_name : Template HTML pour afficher le formulaire.
           success_url : URL de redirection après création réussie.
    """
    form_class = UserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')
