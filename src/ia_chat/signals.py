"""
Signals for ia_chat app
Handles automatic conversation title generation
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Conversation


@receiver(post_save, sender=Message)
def auto_generate_conversation_title(sender, instance, created, **kwargs):
    """
    Auto-generates conversation title from first user message
    Triggered when a new message is saved
    """
    if not created:
        return  # Only for new messages
    
    conversation = instance.conversation
    
    # Only generate if no title and this is a user message
    if not conversation.title and instance.role == 'user':
        # Check if this is the first user message
        first_user_msg = conversation.messages.filter(role='user').order_by('created_at').first()
        
        if first_user_msg and first_user_msg.id == instance.id:
            # Truncate to 50 characters
            title = instance.content[:50] + ('...' if len(instance.content) > 50 else '')
            conversation.title = title
            conversation.save(update_fields=['title'])
