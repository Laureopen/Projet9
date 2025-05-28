from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from django.db.models import Q

class Ticket(models.Model):
    """
        Représente un ticket créé par un utilisateur. Un ticket comprend un titre,
        une description optionnelle, une image optionnelle, ainsi qu'un horodatage
        indiquant la date de création. Chaque ticket est associé à l'utilisateur
        qui l'a créé.
    """
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
            Retourne une représentation lisible du ticket, combinant le titre et l'utilisateur.
        """
        return f"{self.title} - {self.user}"

    def ordered_review_set(self):
        """
            Récupère les critiques liées à ce ticket, ordonnées par date de création décroissante,
            en filtrant uniquement celles écrites par les utilisateurs qui suivent l'auteur du ticket
            sans être bloqués, ou par l'auteur lui-même.

            Retourne :
                QuerySet : Liste filtrée et ordonnée des critiques liées au ticket.
        """

        followers_not_blocked = self.user.followers.filter(is_blocked=False).values_list('user', flat=True)

        return self.review_set.filter(
            Q(user__in=followers_not_blocked) | Q(user=self.user),
            ticket__user=self.user
        ).order_by('-time_created')


class Review(models.Model):
    """
        Représente une critique associée à un ticket.

        Une critique comprend une note (entre 0 et 5), un titre, un corps optionnel,
        une référence à l'utilisateur qui a écrit la critique, ainsi qu'un horodatage
        indiquant la date de création.

        Attributs :
            ticket (ForeignKey) : Le ticket concerné par la critique.
            rating (PositiveSmallIntegerField) : Note attribuée, de 0 à 5 inclus.
            headline (CharField) : Titre de la critique.
            body (CharField) : Texte de la critique (optionnel).
            user (ForeignKey) : Utilisateur auteur de la critique.
            time_created (DateTimeField) : Date et heure de création de la critique.
    """
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    headline = models.CharField(max_length=128)
    body = models.CharField(max_length=8192, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)


class UserFollows(models.Model):
    """
        Modèle représentant la relation de suivi entre deux utilisateurs.

        Permet à un utilisateur de suivre un autre utilisateur. La relation peut être
        bloquée (is_blocked) pour empêcher certaines interactions.

        Attributs :
            user (ForeignKey) : Utilisateur qui suit.
            followed_user (ForeignKey) : Utilisateur suivi.
            is_blocked (BooleanField) : Indique si le suivi est bloqué.

        Contraintes :
            unique_together : Empêche qu'un utilisateur suive plusieurs fois le même utilisateur.
    """
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name='following',
        on_delete=models.CASCADE
    )
    followed_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name='followers',
        on_delete=models.CASCADE
    )
    is_blocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'followed_user')
