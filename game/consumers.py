# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from game.services.game_logic import process_guess
from game.models.game_models import GameSession, Player


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_session_id = self.scope['url_route']['kwargs']['game_session_id']
        self.game_session = GameSession.objects.get(id=self.game_session_id)

        self.player_id = self.scope['user'].id
        self.player = Player.objects.get(id=self.player_id)

        # Join the game room group
        self.group_name = f'game_{self.game_session.id}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the game room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        guess_start = text_data_json['guess_start']
        guess_end = text_data_json['guess_end']
        used_bound = text_data_json['used_bound']

        # Process the guess for the current player
        next_event, score, feedback, is_winner = process_guess(
            self.game_session, self.player, guess_start, guess_end, used_bound
        )

        # Send result back to WebSocket
        await self.send(text_data=json.dumps({
            'score': score,
            'feedback': feedback,
            'is_winner': is_winner,
            'next_event': next_event.title if next_event else None,
        }))

    async def game_update(self, event):
        # Send game update to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))