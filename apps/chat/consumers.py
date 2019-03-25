from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

from chat import models
from utils import methods as utils_methods


class PrivateChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """Connect to WebSocket"""
        self.room_id = self.scope['url_route']['kwargs']['pk']
        self.room_group_name = 'chat_%s' % self.room_id
        self.participants = set()

        # Check if connected user isn't anonymous
        if self.scope['user'].is_anonymous:
            await self.close()
        else:
            # Check user in participants
            qs = models.ChatRoom.objects.by_participant(self.scope['user']).filter(id=self.room_id)
            if qs.exists():
                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                self.participants.add(self.scope['user'].id)
                await self.accept()
            else:
                await self.close()

    async def disconnect(self, close_code):
        """Leave room group"""
        self.participants.remove(self.scope['user'].id)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        """Receive message from WebSocket"""
        try:
            # From web-browser
            message = content['message']
        except:
            # Directly
            message = content

        # Make a record in the DB
        await utils_methods.create_chat_message(room=self.room_id,
                                                message=message,
                                                sender=self.scope['user'])

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': self.scope['user'].get_full_name(),
                'message': message,
                'datetime': f'{timezone.now()}',
                'users': f'{self.participants}'
            }
        )

    async def chat_message(self, event):
        """Receive message from room group"""
        await self.send_json({
            'message': event['message'],
            'datetime': event['datetime'],
            'user': f'{event["user"]}',
            'users': f'{event["users"]}',
        })
