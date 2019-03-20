import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from chat import models


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room']
        self.room_group_name = 'chat_%s' % self.room_id
        # Join room group
        # await self.channel_layer.group_add(
        #     self.room_group_name,
        #     self.channel_name
        # )
        # await self.accept()
        # Check participants
        qs = models.ChatRoom.objects.by_participant(self.scope['user'])
        if qs.exists():
            if qs.first().id == self.room_id:
                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
            else:
                await self.close()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # models.ChatMessage.objects.bulk_create([
        #     models.ChatMessage(sender=,
        #                        recipient=,
        #                        message=message,
        #                        is_read=True,
        #                        room=models.ChatRoom.objects.get(id=self.room_id))
        # ])

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': self.scope['user'].get_full_name(),
                'message': message,
                'datetime': f'{timezone.now()}',
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'datetime': event['datetime'],
            'user': f'{event["user"]}',
        }))
