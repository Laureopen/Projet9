from django.contrib import admin
from reviews.models import Ticket, Review, UserFollows, Comment

admin.site.register(Ticket)
admin.site.register(Review)
admin.site.register(UserFollows)
admin.site.register(Comment)