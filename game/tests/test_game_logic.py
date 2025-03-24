from django.test import TestCase
from django.contrib.auth.models import User
from game.models.event_models import HistoricalEvent
from game.models.game_models import GameSession, Player
from game.services.game_logic import select_random_event, evaluate_guess, start_new_game, process_guess, \
    update_category_and_select_new_event, select_random_user


class GameLogicTestCase(TestCase):
    def setUp(self):
        """Set up test data for players and events."""
        # Create Users for multiple players
        self.user1 = User.objects.create_user(username="TestUser1", password="password")
        self.user2 = User.objects.create_user(username="TestUser2", password="password")

        # Create Players for the users
        self.player1 = Player.objects.create(user=self.user1, username="TestPlayer1")
        self.player2 = Player.objects.create(user=self.user2, username="TestPlayer2")

        self.category1 = "World War II"
        self.category2 = "Cold War"

        # Create sample events with a single year
        self.event1 = HistoricalEvent.objects.create(
            event_description="D-Day",
            event_year=1944,
            category=self.category1
        )
        self.event2 = HistoricalEvent.objects.create(
            event_description="Pearl Harbor Attack",
            event_year=1941,
            category=self.category1
        )

        self.event3 = HistoricalEvent.objects.create(
            event_description="Berlin Airlift",
            event_year=1948,
            category=self.category2
        )

    def test_select_random_event(self):
        """Test that an event is selected from the correct category."""
        event = select_random_event(self.category1)
        self.assertIn(event, [self.event1, self.event2])

    def test_evaluate_guess_correct(self):
        """Test correct guess evaluation."""
        is_correct, score, feedback = evaluate_guess(self.event1, 1944, 1944)
        self.assertTrue(is_correct)
        self.assertEqual(score, 100)
        self.assertEqual(feedback, "Correct! Well played!")

    def test_evaluate_guess_incorrect(self):
        """Test incorrect guess evaluation with score deduction."""
        is_correct, score, feedback = evaluate_guess(self.event1, 1939, 1940)
        self.assertFalse(is_correct)
        self.assertLess(score, 100)
        self.assertIn(feedback, ["Very close!", "Try again!"])

    def test_start_new_game(self):
        """Test that a new game session is created with correct initial values."""
        game_session = start_new_game([self.player1.id], self.category1)
        self.assertIn(self.player1, game_session.players.all() )
        self.assertEqual(game_session.category, self.category1)
        self.assertEqual(len(game_session.remaining_bounds), 7)
        self.assertIsNotNone(game_session.current_event)

    def test_process_guess_correct(self):
        """Test correct guess processing and range bound removal."""
        game_session = start_new_game([self.player1.id], self.category1)
        game_session.current_event = self.event1
        game_session.save()

        next_event, score, feedback, is_winner = process_guess(game_session, 1944, 1944, 7)

        self.assertTrue(score > 0)
        self.assertEqual(feedback, "Correct! Well played!")
        self.assertNotIn(7, game_session.remaining_bounds)

    def test_player_wins_after_all_bounds_used(self):
        """Test that a player wins when all bounds are used up."""
        game_session = start_new_game([self.player1.id], self.category1)
        game_session.current_event = self.event1
        game_session.remaining_bounds = [3]  # Only one bound left
        game_session.save()

        next_event, score, feedback, is_winner = process_guess(game_session, 1944, 1944, 3)

        self.assertTrue(is_winner)
        self.assertEqual(feedback, "You've used all your bounds! You win!")

    def test_update_category_and_select_new_event(self):
        """Test that the category can be updated and a new event selected."""
        game_session = start_new_game([self.player1.id], self.category1)
        game_session.current_event = self.event1
        game_session.save()

        # Update the category to a new one and select a new event for that category
        next_event = update_category_and_select_new_event(game_session, self.category2)

        self.assertEqual(game_session.category, self.category2)
        self.assertEqual(next_event.category, self.category2)
        self.assertIn(next_event, [self.event3])  # Ensure the next event is from the new category

    def test_select_random_user(self):
        """Test that a random user is selected correctly."""
        # Assuming you have a `select_random_user()` method
        game_session = start_new_game([self.player1.id, self.player2.id], self.category1)
        random_user = select_random_user(game_session)
        self.assertIn(random_user, [self.player1, self.player2])
