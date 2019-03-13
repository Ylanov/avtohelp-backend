import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer
from django.utils import timezone


class ChatConsumer(WebsocketConsumer):

    #   WebSocket event handlers

    def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        self.room_group_name = 'user_%s' % self.scope.get('url_route').get('kwargs').get('recipient')
        # # Join room group
        # self.channel_layer.group_add(
        #     self.room_group_name,
        #     self.channel_name
        # )
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        # # Leave room group
        # self.channel_layer.group_discard(
        #     self.room_group_name,
        #     self.channel_name
        # )
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    #   Receive message from WebSocket
    def receive(self, text_data, **kwargs):
        """
        Called when we get a text frame.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # # Send message to room group
        # self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': message,
        #     }
        # )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    #   Receive message from room group
    def chat_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # # Send message to WebSocket
        # self.send(text_data=json.dumps({
        #     'receiver': f'test',
        #     'timestamp': f'{timezone.now().isoformat()}',
        #     'message': message,
        # }))
        self.send(text_data=json.dumps({
            'timestamp': f'{timezone.now().isoformat()}',
            'message': event['message'],
        }))
