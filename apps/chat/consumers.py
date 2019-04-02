from channels.generic.websocket import AsyncJsonWebsocketConsumer

from chat import models
from utils import methods as utils_methods
from utils.api_exceptions import ClientError


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """Connect to WebSocket"""
        # Check if connected user isn't anonymous
        # Are they logged in?
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            # Accept the connection
            await self.accept()
        # Store which rooms the user has joined on this connection
        self.rooms = set()

    async def receive_json(self, content):
        """Receive message from WebSocket"""
        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        # Messages will have a "command" key we can switch on
        command = content.get("command", None)
        try:
            if command == "join":
                # Make them join the room
                await self.join_room(content["room"])
            elif command == "send":
                await self.send_room(content["room"], content["message"])
            elif command == "read":
                await self.read_message(content["room"], content["messages"])
            elif command == "leave":
                # Leave the room
                await self.leave_room(content["room"])
        except ClientError as e:
            # Catch any errors and send it back
            await self.send_json({"error": e.code})

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave all the rooms we are still in
        for room_id in list(self.rooms):
            try:
                await self.leave_room(room_id)
            except ClientError:
                pass

    ##### Command helper methods called by receive_json

    async def join_room(self, room_id):
        """
        Called by receive_json when someone sent a join command.
        """
        # The logged-in user is in our scope thanks to the authentication
        # ASGI middleware
        room = await utils_methods.by_user_and_room_id(self.scope["user"], room_id)
        # Send a join message if it's turned on
        if models.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.join",
                    "room_id": room_id,
                    "user": self.scope["user"].id,
                }
            )
        # Store that we're in the room
        self.rooms.add(room_id)
        # Add them to the group so they get room messages
        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name,
        )
        # Instruct their client to finish opening the room
        await self.send_json({
            "join": room.id,
        })

    async def leave_room(self, room_id):
        """
        Called by receive_json when someone sent a leave command.
        """
        # The logged-in user is in our scope thanks to the authentication
        # ASGI middleware
        room = await utils_methods.by_user_and_room_id(self.scope["user"], room_id)
        # Send a leave message if it's turned on
        if models.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.leave",
                    "room_id": room_id,
                    "user": self.scope["user"].id,
                }
            )
        # Remove that we're in the room
        self.rooms.discard(room_id)
        # Remove them from the group so they no longer get room messages
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name,
        )
        # Instruct their client to finish closing the room
        await self.send_json({
            "leave": room.id,
        })

    async def send_room(self, room_id, message):
        """
        Called by receive_json when someone sends a message to a room.
        """
        # Check they are in this room
        if room_id not in self.rooms:
            raise ClientError("ROOM_ACCESS_DENIED")
        user = self.scope["user"]
        # Get the room and send to the group about it
        room = await utils_methods.by_user_and_room_id(user, room_id)
        # Make a record in the DB
        letter = await utils_methods.create_chat_message(room_id=room_id,
                                                         message=message,
                                                         sender=user)
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.message",
                "room_id": room_id,
                "user": user.id,
                "first_name": user.get_first_name(),
                "last_name": user.get_last_name(),
                "middle_name": user.get_middle_name(),
                "avatar": (user.profile.gallery.filter(is_main=True).first().image['tiny'].url
                           if user.profile.gallery.filter(is_main=True).exists()
                           else None),
                'datetime': f'{letter.created}',
                "message": message,
                "message_id": letter.id
            }
        )

    async def read_message(self, room_id, messages):
        """
        Called by receive_json for read incoming message.
        """
        # Check they are in this room
        if room_id not in self.rooms:
            raise ClientError("ROOM_ACCESS_DENIED")
        # Make a record in the DB
        await utils_methods.read_message(message_list=messages, reader=self.scope["user"])

    ##### Handlers for messages sent over the channel layer

    # These helper methods are named by the types we send - so chat.join
    # becomes chat_join
    async def chat_join(self, event):
        """
        Called when someone has joined our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                "msg_type": models.MSG_TYPE_ENTER,
                "room": event["room_id"],
                "user": event["user"],
            },
        )

    async def chat_leave(self, event):
        """
        Called when someone has left our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                "msg_type": models.MSG_TYPE_LEAVE,
                "room": event["room_id"],
                "user": event["user"],
            },
        )

    async def chat_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                "msg_type": models.MSG_TYPE_MESSAGE,
                "room": event["room_id"],
                "user": event["user"],
                "avatar": event["avatar"],
                "first_name": event["first_name"],
                "last_name": event["last_name"],
                "middle_name": event["middle_name"],
                'datetime': event["datetime"],
                "message": event["message"],
                "message_id": event["message_id"],
            },
        )