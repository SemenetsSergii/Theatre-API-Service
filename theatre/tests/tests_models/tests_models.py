from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from theatre.models import (
    Actor,
    Genre,
    Play,
    Performance,
    Reservation,
    Ticket,
    TheatreHall,
)


class TheatreHallTestCase(TestCase):
    def setUp(self):
        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=40, seats_in_rows=50
        )

    def test_num_seats(self):
        self.assertEqual(self.theatre_hall.num_seats, 2000)


class ActorTestCase(TestCase):
    def setUp(self):
        self.actor = Actor.objects.create(
            first_name="Laurence",
            last_name="Olivier",
            image=SimpleUploadedFile(
                name="test_image.jpg",
                content=b"file_content",
                content_type="image/jpeg",
            ),
        )

    def test_full_name(self):
        self.assertEqual(self.actor.full_name, "Laurence Olivier")


class GenreTestCase(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Ophelia")

    def test_genre_str(self):
        self.assertEqual(str(self.genre), "Ophelia")


class PlayTestCase(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Ophelia")
        self.actor = Actor.objects.create(
            first_name="Laurence",
            last_name="Olivier",
        )
        self.play = Play.objects.create(
            title="Hamlet",
            description="Hamlet is an example of a tragic hero",
            image=SimpleUploadedFile(
                name="play_image.jpg",
                content=b"file_content",
                content_type="image/jpeg",
            ),
        )
        self.play.genre.add(self.genre)
        self.play.actors.add(self.actor)

    def test_play_str(self):
        self.assertEqual(str(self.play), "Hamlet")

    def test_play_genre_and_actors(self):
        self.assertIn(self.genre, self.play.genre.all())
        self.assertIn(self.actor, self.play.actors.all())


class PerformanceTestCase(TestCase):
    def setUp(self):
        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=40, seats_in_rows=50
        )
        self.play = Play.objects.create(
            title="Hamlet", description="Hamlet is an example of a tragic hero"
        )
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time="2024-12-12 19:10"
        )

    def test_performance_str(self):
        self.assertEqual(
            str(self.performance),
            f"{self.play.title} {self.theatre_hall} 2024-12-12 19:10",
        )


class ReservationTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@user.com", password="pass1234"
        )
        self.reservation = Reservation.objects.create(user=self.user)

    def test_reservation_str(self):
        self.assertEqual(str(self.reservation),
                         str(self.reservation.created_at))


class TicketTestCase(TestCase):
    def setUp(self):
        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=20, seats_in_rows=20
        )
        self.play = Play.objects.create(
            title="Hamlet", description="Hamlet is an example of a tragic hero"
        )
        self.performance = Performance.objects.create(
            play=self.play, theatre_hall=self.theatre_hall,
            show_time="2024-12-12 19:10"
        )
        self.user = get_user_model().objects.create_user(
            email="test@user.com", password="pass1234"
        )
        self.reservation = Reservation.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            row=10,
            seat=15,
            performance=self.performance,
            reservation=self.reservation,
            user=self.user,
        )

    def test_ticket_str(self):
        self.assertEqual(str(self.ticket),
                         f"{self.performance}"
                         f" (row: 10, seat: 15)")

    def test_ticket_validation(self):
        try:
            self.ticket.clean()
        except ValidationError:
            self.fail("Valid ticket raised ValidationError")
        invalid_ticket = Ticket(
            row=20,
            seat=20,
            performance=self.performance,
            reservation=self.reservation,
            user=self.user,
        )
        with self.assertRaises(ValidationError):
            invalid_ticket.clean()
