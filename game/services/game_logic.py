# game/services/game_logic.py
import random
from game.models.event_models import HistoricalEvent
from game.models.game_models import GameSession, Player

def select_random_event(category):
    """Fetch a random historical event from the specified category."""
    return HistoricalEvent.objects.filter(category=category).order_by("?").first()

def select_random_user(game_session):
    """Select a random player from the active players in the game session."""
    players = game_session.players.all()  # Or restrict it to the players currently in the game
    random_user = random.choice(players)  # Randomly select a user
    return random_user
def start_new_game(player_ids, category):
    """Initialize a new game session for a player with a chosen category."""
    players = [Player.objects.get(id=player_id) for player_id in player_ids]
    game_session = GameSession.objects.create(category=category)
    game_session.players.set(players)

    # Assign 7 unique year range bounds (can be any values between min/max range)
    game_session.remaining_bounds = list(range(1, 8))  # Players must use up these bounds
    game_session.save()

    # Initialize the first event with the selected category
    first_event = select_random_event(category)  # Select the first event for the session
    game_session.current_event = first_event
    game_session.save()

    return game_session

def process_guess(game_session, guess_start, guess_end, used_bound):
    """
    Process player's guess, update their remaining bounds, and check for a winner.
    """
    event = game_session.current_event
    if not event:
        return None, 0, "No active event found.", False

    # Validate the used bound
    if used_bound not in game_session.remaining_bounds:
        return event, 0, "Invalid range bound. Pick from your remaining bounds.", False

    # Evaluate the guess
    is_correct, score, feedback = evaluate_guess(event, guess_start, guess_end)

    if is_correct:
        game_session.remaining_bounds.remove(used_bound)  # Remove used bound if correct
        game_session.save()

        # Check if the player has won
        if not game_session.remaining_bounds:
            return None, score, "You've used all your bounds! You win!", True

    # Don't select next event until the category is updated (after guessing is processed)
    return event, score, feedback, False

def update_category_and_select_new_event(game_session, new_category):
    """Update the category and select a new event based on the new category."""
    game_session.category = new_category
    game_session.save()

    # Select the next event after category change
    next_event = select_random_event(new_category)
    game_session.current_event = next_event
    game_session.save()

    return next_event

def evaluate_guess(event, guess_start, guess_end):
    """
    Compare player's guess with the actual event date.

    :param event: HistoricalEvent instance
    :param guess_start: Player's guessed start year
    :param guess_end: Player's guessed end year
    :return: (is_correct, score, feedback)
    """
    actual_year = event.event_year

    is_correct = guess_start <= actual_year <= guess_end
    score = 100 if is_correct else max(0, 100 - (abs(guess_start - actual_year)))

    if is_correct:
        feedback = "Correct! Well played!"
    elif abs(guess_start - actual_year) <= 5:
        feedback = "Very close!"
    else:
        feedback = "Try again!"

    return is_correct, score, feedback