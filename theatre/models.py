import pathlib
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_rows = models.IntegerField()

    class Meta:
        verbose_name_plural = "theatre halls"

    def __str__(self):
        return self.name

    @property
    def num_seats(self):
        return self.seats_in_rows * self.rows


def create_custom_path(instance, filename):
    if isinstance(instance, Actor):
        directory = "actors"
        name_slug = slugify(f"{instance.first_name}-{instance.last_name}")
    elif isinstance(instance, Play):
        directory = "plays"
        name_slug = slugify(instance.title)
    else:
        directory = "uploads"
        name_slug = slugify(instance.__class__.__name__)

    filename = f"{name_slug}-{uuid.uuid4()}{pathlib.Path(filename).suffix}"
    return pathlib.Path(f"upload/{directory}/") / pathlib.Path(filename)


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=create_custom_path, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genre = models.ManyToManyField(
        Genre,
        related_name='plays',
        blank=True)
    actors = models.ManyToManyField(
        Actor,
        related_name='plays',
        blank=True
    )
    image = models.ImageField(upload_to=create_custom_path, blank=True, null=True)

    def __str__(self):
        return self.title


class Performance(models.Model):
    play = models.ForeignKey(
        Play,
        related_name='performances',
        on_delete=models.CASCADE
    )
    theatre_hall = models.ForeignKey(
        TheatreHall,
        related_name='performances',
        on_delete=models.CASCADE
    )
    show_time = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["play", "theatre_hall"]),
            models.Index(fields=["show_time"]),
        ]

    def __str__(self):
        return f"{self.play.title} {self.theatre_hall} {str(self.show_time)}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(
        Performance,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name='tickets',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
    )

    def __str__(self):
        return f"{str(self.performance)} (row: {self.row}, seat: {self.seat})"

    class Meta:
        unique_together = ("performance", "row", "seat")
        ordering = ["row", "seat"]

    @staticmethod
    def validate_ticket(row, seat, cinema_hall, error_to_raise):
        for ticket_attr_value, ticket_attr_name, cinema_hall_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_rows"),
        ]:
            count_attrs = getattr(cinema_hall, cinema_hall_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} number "
                        f"must be in available range: "
                        f"(1, {cinema_hall_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.performance.theatre_hall,
            ValidationError,
        )

    def save(
        self,
        force_update=False,
        force_insert=False,
        using=None,
        update_fields=None
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert,
            force_update,
            using,
            update_fields
        )

    class Meta:
        ordering = ["id"]