import pathlib
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
    )

    def __str__(self):
        return str(self.created_at)


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_rows = models.IntegerField()

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

    def __str__(self):
        return f"{self.play.title} {str(self.show_time)}"


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

    def __str__(self):
        return f"{str(self.performance)} (row: {self.row}, seat: {self.seat})"
