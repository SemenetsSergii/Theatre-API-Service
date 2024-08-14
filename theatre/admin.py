from django.contrib import admin

from theatre.models import (
    Actor,
    Genre,
    Play,
    Performance,
    Reservation,
    TheatreHall,
    Ticket,
)

admin.site.register(Actor)
admin.site.register(Genre)
admin.site.register(Play)
admin.site.register(Performance)
admin.site.register(Reservation)
admin.site.register(TheatreHall)
admin.site.register(Ticket)
