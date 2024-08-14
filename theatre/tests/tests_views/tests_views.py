from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from theatre.models import (
    Actor,
    Genre,
    Play,
    Performance,
    Ticket,
    TheatreHall,
    Reservation
)
from theatre.serializers import (
    ActorSerializer,
    GenreSerializer,
    PlayDetailSerializer,
    PlayListSerializer,
    TicketSerializer,
    TheatreHallSerializer,
    ReservationListSerializer
)
from user.models import User

ACTOR_URL = reverse("theatre:actor-list")
GENRE_URL = reverse("theatre:genre-list")
PLAY_URL = reverse("theatre:play-list")
PERFORMANCE_URL = reverse("theatre:performance-list")
THEATRE_HALL_URL = reverse("theatre:theatre_hall-list")
RESERVATION_URL = reverse("theatre:reservation-list")
TICKET_URL = reverse("theatre:ticket-list")


class ActorViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)
        self.admin = get_user_model().objects.create_superuser(
            email="admin@test.com", password="adminpassword"
        )

    def test_list_actors(self):
        Actor.objects.create(first_name="Tom", last_name="Hanks")
        Actor.objects.create(first_name="Leonardo", last_name="DiCaprio")
        response = self.client.get(ACTOR_URL)
        actors = Actor.objects.all()
        serializer = ActorSerializer(actors, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_actor_authenticated(self):
        self.client.force_authenticate(self.admin)
        payload = {"first_name": "Brad", "last_name": "Pitt"}
        response = self.client.post(ACTOR_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        actor = Actor.objects.get(id=response.data["id"])
        self.assertEqual(actor.first_name, payload["first_name"])
        self.assertEqual(actor.last_name, payload["last_name"])

    def test_create_actor_unauthenticated(self):
        self.client.logout()
        payload = {"first_name": "Brad", "last_name": "Pitt"}
        response = self.client.post(ACTOR_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GenreViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)
        self.admin = get_user_model().objects.create_superuser(
            email="admin@test.com", password="adminpassword"
        )

    def test_list_genres(self):
        Genre.objects.create(name="Comedy")
        Genre.objects.create(name="Drama")
        response = self.client.get(GENRE_URL)
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_genre_authenticated(self):
        self.client.force_authenticate(self.admin)
        payload = {"name": "Thriller"}
        response = self.client.post(GENRE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        genre = Genre.objects.get(id=response.data["id"])
        self.assertEqual(genre.name, payload["name"])

    def test_create_genre_unauthenticated(self):
        self.client.logout()
        payload = {"name": "Thriller"}
        response = self.client.post(GENRE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PlayViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)
        self.admin = get_user_model().objects.create_superuser(
            email="admin@test.com", password="adminpassword"
        )
        self.genre = Genre.objects.create(name="Drama")
        self.actor = Actor.objects.create(first_name="Tom", last_name="Hanks")

    def test_list_plays(self):
        Play.objects.create(title="Play 1")
        Play.objects.create(title="Play 2")
        response = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_play_unauthenticated(self):
        self.client.logout()
        payload = {
            "title": "New Play",
            "duration": 90,
        }
        response = self.client.post(PLAY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_plays_by_title(self):
        Play.objects.create(title="Play 1")
        Play.objects.create(title="Play 2")
        response = self.client.get(PLAY_URL, {"title": "Play 1"})
        play = Play.objects.get(title="Play 1")
        serializer = PlayDetailSerializer(play)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, response.data)

    def test_filter_plays_by_genres(self):
        play = Play.objects.create(title="Play 1")
        play.genre.add(self.genre)
        response = self.client.get(PLAY_URL, {"genre": self.genre.id})
        expected_data = {
            "id": play.id,
            "title": "Play 1",
            "description": "",
            "genre": [self.genre.name],
            "actors": [],
            "image": None,
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(expected_data, response.data)

    def test_filter_plays_by_actors(self):
        play = Play.objects.create(title="Play 1")
        play.actors.add(self.actor)
        response = self.client.get(PLAY_URL, {"actors": self.actor.id})
        expected_data = {
            "id": play.id,
            "title": "Play 1",
            "description": "",
            "genre": [],
            "actors": [self.actor.full_name],
            "image": None,
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(expected_data, response.data)


class PerformanceViewSetTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            email="admin@example.com", password="password123"
        )
        self.play = Play.objects.create(title="Play 1")
        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", seats_in_rows=50, rows=20
        )
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time="2024-08-10T19:00:00Z",
        )

    def test_list_performance_as_authenticated_user(self):
        response = self.client.get(PERFORMANCE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_performance_anonymous(self):
        self.client.logout()
        response = self.client.get(PERFORMANCE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_performance_authenticated(self):
        self.client.force_authenticate(self.admin)
        payload = {
            "play": self.play.id,
            "theatre_hall": self.theatre_hall.id,
            "show_time": "2024-08-10T19:00:00+03:00",
        }
        response = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["play"], self.play.id)
        self.assertEqual(response.data["theatre_hall"], self.theatre_hall.id)
        self.assertEqual(response.data["show_time"],
                         "2024-08-10T19:00:00+03:00")

    def test_create_performance_unauthenticated(self):
        self.client.logout()
        payload = {"play": self.play.id, "theatre_hall": self.theatre_hall.id}
        response = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_performance_authenticated(self):
        url = reverse("theatre:performance-detail", args=[self.performance.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_performance_authenticated(self):
        url = reverse("theatre:performance-detail", args=[self.performance.id])
        payload = {"play": self.play.id}
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_performance_authenticated(self):
        url = reverse("theatre:performance-detail", args=[self.performance.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TheatreHallViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)
        self.admin = get_user_model().objects.create_superuser(
            email="admin@test.com", password="adminpassword"
        )
        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", seats_in_rows=50, rows=200
        )

    def test_list_theatre_halls_as_authenticated_user(self):
        response = self.client.get(THEATRE_HALL_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        theatre_halls = TheatreHall.objects.all()
        serializer = TheatreHallSerializer(theatre_halls, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_list_theatre_halls_anonymous(self):
        self.client.logout()
        response = self.client.get(THEATRE_HALL_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        expected_error = {
            "detail": "Authentication credentials were not provided."
        }
        self.assertEqual(response.data, expected_error)

    def test_create_theatre_hall_unauthenticated(self):
        self.client.logout()
        payload = {"name": "New Hall", "num_seats": 200}
        response = self.client.post(THEATRE_HALL_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_theatre_hall_authenticated(self):
        url = reverse("theatre:theatre_hall-detail",
                      args=[self.theatre_hall.id])
        response = self.client.get(url)
        serializer = TheatreHallSerializer(self.theatre_hall)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_theatre_hall_authenticated(self):
        self.client.force_authenticate(self.admin)
        url = reverse("theatre:theatre_hall-detail",
                      args=[self.theatre_hall.id])
        payload = {"name": "Updated Hall", "num_seats": 10000}
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.theatre_hall.refresh_from_db()
        self.assertEqual(self.theatre_hall.name, payload["name"])
        self.assertEqual(self.theatre_hall.num_seats, payload["num_seats"])

    def test_update_theatre_hall_unauthenticated(self):
        url = reverse("theatre:theatre_hall-detail",
                      args=[self.theatre_hall.id])
        payload = {"name": "Updated Hall", "num_seats": 150}
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_theatre_hall_authenticated(self):
        self.client.force_authenticate(self.admin)
        url = reverse("theatre:theatre_hall-detail",
                      args=[self.theatre_hall.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            TheatreHall.objects.filter(
                id=self.theatre_hall.id).exists())

    def test_delete_theatre_hall_unauthenticated(self):
        url = reverse("theatre:theatre_hall-detail",
                      args=[self.theatre_hall.id])
        self.client.logout()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TicketViewSetTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com", password="testpass"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", password="testpass"
        )
        self.client.force_authenticate(self.user)

        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_rows=10
        )
        self.play = Play.objects.create(title="Hamlet")
        self.performance = Performance.objects.create(
            play=self.play,
            theatre_hall=self.theatre_hall,
            show_time="2024-08-15 19:00:00",
        )
        self.reservation = Reservation.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            performance=self.performance,
            reservation=self.reservation,
            row=1,
            seat=1,
            user=self.user,
        )

    def test_list_tickets(self):
        response = self.client.get(TICKET_URL)
        tickets = Ticket.objects.filter(reservation__user=self.user)
        serializer = TicketSerializer(tickets, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_tickets_other_user(self):
        Ticket.objects.create(
            performance=self.performance,
            reservation=Reservation.objects.create(user=self.other_user),
            seat=2,
            row=2,
            user=self.other_user,
        )
        self.client.force_authenticate(self.user)
        response = self.client.get(TICKET_URL)
        tickets = Ticket.objects.filter(reservation__user=self.user)
        serializer = TicketSerializer(tickets, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_ticket_invalid_reservation(self):
        other_reservation = Reservation.objects.create(user=self.other_user)
        payload = {
            "performance": self.performance.id,
            "reservation": other_reservation.id,
            "seat": -100,
        }
        response = self.client.post(TICKET_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ticket(self):
        url = reverse("theatre:ticket-detail", args=[self.ticket.id])
        response = self.client.get(url)
        serializer = TicketSerializer(self.ticket)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_delete_ticket(self):
        url = reverse("theatre:ticket-detail", args=[self.ticket.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ticket.objects.filter(id=self.ticket.id).exists())


class ReservationViewSetTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com", password="testpassword"
        )
        self.admin = get_user_model().objects.create_superuser(
            email="admin@test.com", password="adminpassword"
        )

        self.theatre_hall = TheatreHall.objects.create(
            name="Main Hall", rows=10, seats_in_rows=10
        )
        self.play = Play.objects.create(
            title="Test Play", description="Test Description"
        )
        show_time = (timezone.now()
                     + timezone.timedelta(days=1))
        self.performance = Performance.objects.create(
            play=self.play, theatre_hall=self.theatre_hall, show_time=show_time
        )
        self.reservation = Reservation.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            reservation=self.reservation,
            performance=self.performance,
            row=1,
            seat=1,
            user=self.user,
        )
        self.client.force_authenticate(self.user)

    def test_list_reservations(self):
        response = self.client.get(RESERVATION_URL)
        reservations = Reservation.objects.filter(user=self.user)
        serializer = ReservationListSerializer(reservations, many=True)
        response_data = response.json()
        actual_data = response_data.get("results", [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(actual_data, serializer.data)

    def test_create_reservation(self):
        payload = {
            "tickets": [
                {
                    "performance": self.performance.id,
                    "seat_row": 1,
                    "seat_number": 1,
                }
            ]
        }
        response = self.client.post(RESERVATION_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_create_reservation_unauthenticated(self):
        self.client.force_authenticate(user=None)
        payload = {
            "tickets": [
                {
                    "performance": self.performance.id,
                    "seat_row": 1,
                    "seat_number": 1,
                }
            ]
        }
        response = self.client.post(RESERVATION_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_reservations_as_other_user(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(RESERVATION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
