import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

User = get_user_model()


def send_notification_to_user(user_id, notification_data):
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'notifications_user_{user_id}',
            {
                'type': 'notification_event',
                'data': notification_data
            }
        )


def send_notification_to_role(role, notification_data):
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'notifications_role_{role}',
            {
                'type': 'notification_event',
                'data': notification_data
            }
        )


def send_message_to_user(user_id, message_data):
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f'notifications_user_{user_id}',
            {
                'type': 'message_event',
                'data': message_data
            }
        )


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.user_group_name = f'notifications_user_{self.user.id}'
        self.role_group_name = f'notifications_role_{self.user.role}'

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.role_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user and self.user.is_authenticated:
            await self.channel_layer.group_discard(
                f'notifications_user_{self.user.id}',
                self.channel_name
            )
            await self.channel_layer.group_discard(
                f'notifications_role_{self.user.role}',
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'mark_read':
            notification_id = data.get('notification_id')
            if notification_id:
                await self.mark_notification_read(notification_id)

    async def notification_event(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data']
        }))

    async def message_event(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'data': event['data']
        }))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        from authentification.models import Notification
        try:
            notification = Notification.objects.get(id=notification_id, destinataire=self.user)
            notification.est_lu = True
            notification.save(update_fields=['est_lu'])
        except Notification.DoesNotExist:
            pass


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.room_group_name = f'chat_user_{self.user.id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'typing':
            await self.handle_typing(data)
        elif message_type == 'read':
            await self.handle_read(data)

    async def handle_chat_message(self, data):
        conversation_id = data.get('conversation_id')
        content = data.get('message', '').strip()

        if not content or not conversation_id:
            return

        message = await self.save_message(conversation_id, content)
        if message:
            conversation_group = f'conversation_{conversation_id}'

            await self.channel_layer.group_send(
                conversation_group,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'contenu': message.contenu,
                        'auteur': {
                            'id': self.user.id,
                            'name': self.user.get_full_name() or self.user.username,
                        },
                        'date_envoi': message.date_envoi.isoformat(),
                        'est_lu': False
                    },
                    'conversation_id': conversation_id,
                    'sender_id': self.user.id
                }
            )

    async def handle_typing(self, data):
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing', False)

        await self.channel_layer.group_send(
            f'conversation_{conversation_id}',
            {
                'type': 'typing',
                'user_id': self.user.id,
                'user_name': self.user.get_full_name() or self.user.username,
                'is_typing': is_typing,
                'conversation_id': conversation_id
            }
        )

    async def handle_read(self, data):
        conversation_id = data.get('conversation_id')
        message_id = data.get('message_id')

        await self.mark_as_read(message_id)

        await self.channel_layer.group_send(
            f'conversation_{conversation_id}',
            {
                'type': 'message_read',
                'message_id': message_id,
                'reader_id': self.user.id,
                'conversation_id': conversation_id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'conversation_id': event.get('conversation_id'),
            'sender_id': event['sender_id']
        }))

    async def typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'is_typing': event['is_typing'],
            'conversation_id': event.get('conversation_id')
        }))

    async def message_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id'],
            'reader_id': event['reader_id'],
            'conversation_id': event.get('conversation_id')
        }))

    @database_sync_to_async
    def save_message(self, conversation_id, content):
        from authentification.models import Conversation, Message
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            if not conversation.participants.filter(id=self.user.id).exists():
                return None

            other_user = conversation.get_other_participant(self.user)

            message = Message.objects.create(
                auteur=self.user,
                destinataire=other_user if not conversation.is_groupe else None,
                conversation=conversation,
                contenu=content,
                type_message='groupe' if conversation.is_groupe else 'individuel'
            )
            conversation.updated_at = message.date_envoi
            conversation.save(update_fields=['updated_at'])
            
            for participant in conversation.participants.exclude(id=self.user.id):
                send_message_to_user(participant.id, {
                    'type': 'message',
                    'titre': 'Nouveau message',
                    'message': content[:100],
                    'conversation_id': conversation.id,
                    'lien': f'/authentification/messages/{conversation.id}/',
                    'auteur': {
                        'id': self.user.id,
                        'name': self.user.get_full_name() or self.user.username,
                    },
                    'date_creation': message.date_envoi.isoformat()
                })
            
            return message
        except Conversation.DoesNotExist:
            return None

    @database_sync_to_async
    def mark_as_read(self, message_id):
        from authentification.models import Message
        try:
            message = Message.objects.select_related('conversation').get(id=message_id)
            if message.conversation and message.conversation.participants.filter(id=self.user.id).exists():
                message.est_lu = True
                message.save(update_fields=['est_lu'])
        except Message.DoesNotExist:
            pass


class ConversationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'conversation_{self.conversation_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({'type': 'connection_established', 'conversation_id': self.conversation_id}))

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'typing':
            await self.handle_typing(data)
        elif message_type == 'read':
            await self.handle_read(data)

    async def handle_chat_message(self, data):
        content = data.get('message', '').strip()
        if not content:
            return

        message = await self.save_message(content)
        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'contenu': message.contenu,
                        'auteur': {
                            'id': self.user.id,
                            'name': self.user.get_full_name() or self.user.username,
                        },
                        'date_envoi': message.date_envoi.isoformat(),
                        'est_lu': False
                    },
                    'conversation_id': self.conversation_id,
                    'sender_id': self.user.id
                }
            )

    async def handle_typing(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing',
                'user_id': self.user.id,
                'user_name': self.user.get_full_name() or self.user.username,
                'is_typing': data.get('is_typing', False),
                'conversation_id': self.conversation_id
            }
        )

    async def handle_read(self, data):
        message_id = data.get('message_id')
        if not message_id:
            return

        await self.mark_as_read(message_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_read',
                'message_id': message_id,
                'reader_id': self.user.id,
                'conversation_id': self.conversation_id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'conversation_id': event.get('conversation_id'),
            'sender_id': event['sender_id']
        }))

    async def typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'is_typing': event['is_typing'],
            'conversation_id': event.get('conversation_id')
        }))

    async def message_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id'],
            'reader_id': event['reader_id'],
            'conversation_id': event.get('conversation_id')
        }))

    @database_sync_to_async
    def save_message(self, content):
        from authentification.models import Conversation, Message
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            if not conversation.participants.filter(id=self.user.id).exists():
                return None

            other_user = conversation.get_other_participant(self.user)

            message = Message.objects.create(
                auteur=self.user,
                destinataire=other_user if not conversation.is_groupe else None,
                conversation=conversation,
                contenu=content,
                type_message='groupe' if conversation.is_groupe else 'individuel'
            )
            conversation.updated_at = message.date_envoi
            conversation.save(update_fields=['updated_at'])
            
            for participant in conversation.participants.exclude(id=self.user.id):
                send_message_to_user(participant.id, {
                    'type': 'message',
                    'titre': 'Nouveau message',
                    'message': content[:100],
                    'conversation_id': conversation.id,
                    'lien': f'/authentification/messages/{conversation.id}/',
                    'auteur': {
                        'id': self.user.id,
                        'name': self.user.get_full_name() or self.user.username,
                    },
                    'date_creation': message.date_envoi.isoformat()
                })
            
            return message
        except Conversation.DoesNotExist:
            return None

    @database_sync_to_async
    def mark_as_read(self, message_id):
        from authentification.models import Message
        try:
            message = Message.objects.select_related('conversation').get(id=message_id)
            if message.conversation and message.conversation.participants.filter(id=self.user.id).exists():
                message.est_lu = True
                message.save(update_fields=['est_lu'])
        except Message.DoesNotExist:
            pass
