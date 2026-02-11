"""
WebSocket Consumer for real-time AI chat
Handles bidirectional communication between client and LLM
"""
import json
import logging
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from .models import Conversation, Message, ConversationPreference
from .service.llm_service import LLMService

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for AI chat
    Handles: connection, message sending, streaming responses
    """
    
    async def connect(self):
        """
        Called when WebSocket connection is established
        Accepts authenticated users only
        """
        self.user = self.scope['user']
        
        # Reject anonymous users
        if isinstance(self.user, AnonymousUser):
            await self.close(code=4001)
            logger.warning("Anonymous user attempted to connect")
            return
        
        # Get conversation_id from URL route
        self.conversation_id = self.scope['url_route']['kwargs'].get('conversation_id')
        
        # Verify conversation exists and belongs to user
        if self.conversation_id:
            try:
                self.conversation = await self.get_conversation(self.conversation_id)
                if self.conversation.user_id != self.user.id:
                    await self.close(code=4003)
                    logger.warning(f"User {self.user.id} tried to access conversation {self.conversation_id}")
                    return
            except Conversation.DoesNotExist:
                await self.close(code=4004)
                logger.warning(f"Conversation {self.conversation_id} not found")
                return
        else:
            self.conversation = None
        
        # Accept connection
        await self.accept()
        logger.info(f"User {self.user.username} connected (conversation: {self.conversation_id})")
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'conversation_id': self.conversation_id,
            'message': 'Connected successfully'
        }))
    
    async def disconnect(self, close_code):
        """Called when WebSocket connection is closed"""
        logger.info(f"User {self.user.username} disconnected (code: {close_code})")
    
    async def receive(self, text_data):
        """
        Called when message is received from WebSocket
        Handles: user messages, commands (new_conversation, load_history)
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_user_message(data)
            elif message_type == 'new_conversation':
                await self.handle_new_conversation(data)
            elif message_type == 'load_history':
                await self.handle_load_history(data)
            else:
                await self.send_error(f"Unknown message type: {message_type}")
        
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error in receive: {e}", exc_info=True)
            await self.send_error(f"Server error: {str(e)}")
    
    async def handle_user_message(self, data):
        """
        Process user message and generate AI response
        """
        user_content = data.get('content', '').strip()
        
        if not user_content:
            await self.send_error("Message content cannot be empty")
            return
        
        # Create conversation if not exists
        if not self.conversation:
            self.conversation = await self.create_conversation()
            await self.send(text_data=json.dumps({
                'type': 'conversation_created',
                'conversation_id': self.conversation.id
            }))
        
        # Save user message
        user_message = await self.save_message(
            conversation=self.conversation,
            role='user',
            content=user_content
        )
        
        # Send confirmation that message was received
        await self.send(text_data=json.dumps({
            'type': 'message_received',
            'message_id': user_message.id,
            'content': user_content,
            'timestamp': user_message.created_at.isoformat()
        }))
        
        # Generate AI response
        await self.generate_ai_response(user_content)
    
    async def generate_ai_response(self, user_content: str):
        """
        Generate AI response using LLM service
        Supports streaming for real-time display
        """
        try:
            # Get user preferences
            prefs = await self.get_user_preferences()
            
            # Build context messages
            context_messages = await self.get_context_messages(
                max_messages=prefs.max_context_messages
            )
            
            # Add current user message
            messages = context_messages + [{'role': 'user', 'content': user_content}]
            
            # Send "thinking" status
            await self.send(text_data=json.dumps({
                'type': 'assistant_thinking',
                'message': 'Generating response...'
            }))
            
            # Generate response (with streaming)
            start_time = time.time()
            full_response = ""
            token_count = 0
            
            # Run LLM in thread pool (blocking operation)
            response_generator = await database_sync_to_async(LLMService.chat)(
                messages=messages,
                model_key=self.conversation.model_used,
                max_tokens=prefs.max_tokens,
                temperature=prefs.temperature,
                stream=True
            )
            
            # Stream response chunks
            async for chunk in self._async_generator(response_generator):
                full_response += chunk
                token_count += 1
                
                await self.send(text_data=json.dumps({
                    'type': 'assistant_chunk',
                    'content': chunk
                }))
            
            generation_time = time.time() - start_time
            
            # Save assistant message
            assistant_message = await self.save_message(
                conversation=self.conversation,
                role='assistant',
                content=full_response,
                tokens_used=token_count,
                generation_time=generation_time
            )
            
            # Send completion signal
            await self.send(text_data=json.dumps({
                'type': 'assistant_complete',
                'message_id': assistant_message.id,
                'content': full_response,
                'tokens_used': token_count,
                'generation_time': round(generation_time, 2),
                'timestamp': assistant_message.created_at.isoformat()
            }))
        
        except Exception as e:
            logger.error(f"Error generating AI response: {e}", exc_info=True)
            await self.send_error(f"Failed to generate response: {str(e)}")
    
    async def handle_new_conversation(self, data):
        """Create a new conversation"""
        model_key = data.get('model', 'llama3')
        enable_history = data.get('enable_history', True)
        
        self.conversation = await self.create_conversation(
            model_used=model_key,
            enable_history=enable_history
        )
        
        await self.send(text_data=json.dumps({
            'type': 'conversation_created',
            'conversation_id': self.conversation.id,
            'model': model_key,
            'enable_history': enable_history
        }))
    
    async def handle_load_history(self, data):
        """Load conversation history"""
        if not self.conversation:
            await self.send_error("No active conversation")
            return
        
        messages = await self.get_all_messages()
        
        await self.send(text_data=json.dumps({
            'type': 'history_loaded',
            'messages': [
                {
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                    'tokens_used': msg.tokens_used,
                    'generation_time': msg.generation_time
                }
                for msg in messages
            ]
        }))
    
    async def send_error(self, error_message: str):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message
        }))
    
    # Database operations (async wrappers)
    
    @database_sync_to_async
    def get_conversation(self, conversation_id):
        """Get conversation by ID"""
        return Conversation.objects.get(id=conversation_id)
    
    @database_sync_to_async
    def create_conversation(self, model_used='llama3', enable_history=True):
        """Create new conversation"""
        return Conversation.objects.create(
            user=self.user,
            model_used=model_used,
            enable_history=enable_history
        )
    
    @database_sync_to_async
    def save_message(self, conversation, role, content, tokens_used=None, generation_time=None):
        """Save message to database"""
        return Message.objects.create(
            conversation=conversation,
            role=role,
            content=content,
            tokens_used=tokens_used,
            generation_time=generation_time
        )
    
    @database_sync_to_async
    def get_user_preferences(self):
        """Get or create user preferences"""
        prefs, _ = ConversationPreference.objects.get_or_create(
            user=self.user,
            defaults={
                'default_model': 'llama3',
                'temperature': 0.7,
                'max_tokens': 512,
                'max_context_messages': 10
            }
        )
        return prefs
    
    @database_sync_to_async
    def get_context_messages(self, max_messages=10):
        """Get conversation context for LLM"""
        return self.conversation.get_context_messages(max_messages)
    
    @database_sync_to_async
    def get_all_messages(self):
        """Get all messages in conversation"""
        return list(self.conversation.messages.all())
    
    # Utility methods
    
    async def _async_generator(self, sync_generator):
        """Convert sync generator to async generator"""
        def get_next():
            try:
                return next(sync_generator)
            except StopIteration:
                return None
        
        while True:
            chunk = await database_sync_to_async(get_next)()
            if chunk is None:
                break
            yield chunk
