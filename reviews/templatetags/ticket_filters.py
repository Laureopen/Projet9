from django import template
from reviews.models import UserFollows

register = template.Library()

@register.filter
def can_be_reviewed_by(ticket, user):
    if not user.is_authenticated:
        return False
    return UserFollows.objects.filter(
        user=ticket.user,
        followed_user=user,
        is_blocked=False
    ).exists()