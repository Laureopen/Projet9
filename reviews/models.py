from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from django.db.models import Q

class Ticket(models.Model):
    """
    Represents a ticket created by a user. A ticket includes a title,
    an optional description, an optional image, and a timestamp indicating
    when it was created. Each ticket is linked to the user who created it.
    """
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    asked_review = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.user}"

    def ordered_review_set(self):
        # Affiche les utilisateurs qui suivent l'utilisateur courant
        followers_not_blocked = self.user.followers.filter(is_blocked=False).values_list('user', flat=True)
        # Filtrer les critiques où l'auteur fait partie des followers non bloqués
        # et où le ticket appartient à l'utilisateur courant
        return self.review_set.filter(
            Q(user__in=followers_not_blocked) | Q(user=self.user),
            ticket__user=self.user  # Le ticket doit être créé par l'utilisateur courant
        ).order_by('-time_created')  # Tri des critiques de la plus récente à la plus ancienne


class Review(models.Model):
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    headline = models.CharField(max_length=128)
    body = models.CharField(max_length=8192, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)


class UserFollows(models.Model):
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
