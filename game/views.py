from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from game.services.game_logic import start_new_game, process_guess, select_random_user
from game.models.game_models import GameSession, Player

# game/views.py
from django.shortcuts import render

def index(request):
    # Your logic here (rendering a template, processing request, etc.)
    return render(request, 'index.html')
@login_required
def start_game(request):
    """Handle the start of a new game."""
    if request.method == 'POST':
        category = request.POST.get('category')
        game_session = start_new_game(request.user.id, category)
        return redirect('play_game', game_session_id=game_session.id)

    return render(request, 'game/select_category.html')

@login_required
def play_game(request, game_session_id):
    """Handle the ongoing game play, including guesses and event processing."""
    game_session = GameSession.objects.get(id=game_session_id)

    if request.method == 'POST':
        guess_start = int(request.POST.get('guess_start'))
        guess_end = int(request.POST.get('guess_end'))
        used_bound = int(request.POST.get('used_bound'))

        # Process the guess, no category change here
        next_event, score, feedback, is_winner = process_guess(game_session, guess_start, guess_end, used_bound)

        if is_winner:
            # If the player wins, ask a random user to select the next category
            random_user = select_random_user()  # Get a random user for category selection
            return redirect('select_category_for_next_round', random_user_id=random_user.id)

        return render(request, 'game/play_game.html', {
            'game_session': game_session,
            'next_event': next_event,
            'score': score,
            'feedback': feedback,
        })

    return render(request, 'game/play_game.html', {'game_session': game_session})

@login_required
def select_category_for_next_round(request, random_user_id):
    """Allow the random user to select the category for the next round."""
    random_user = Player.objects.get(id=random_user_id)

    if request.method == 'POST':
        # When the random user selects the category
        category = request.POST.get('category')
        game_session = GameSession.objects.get(id=request.session.get('game_session_id'))
        game_session.category = category  # Update the category for the next round
        game_session.save()

        return redirect('play_game', game_session_id=game_session.id)

    return render(request, 'game/select_category_for_next_round.html', {'random_user': random_user})
