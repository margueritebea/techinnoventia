"""
Django models for AI chatbot
Manages conversations and messages with history support
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Conversation(models.Model):
    """
    Conversation between a user and the AI
    A conversation = set of exchanged messages
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ia_conversations',
        verbose_name=_("User")
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Title"),
        help_text=_("Auto-generated from first message if empty")
    )
    model_used = models.CharField(
        max_length=50,
        default='llama3',
        verbose_name=_("AI Model"),
        help_text=_("Model key used (llama3, mistral, qwen)")
    )
    enable_history = models.BooleanField(
        default=True,
        verbose_name=_("Enable History"),
        help_text=_("If False, each message is processed without context")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )
    
    class Meta:
        verbose_name = _("AI Conversation")
        verbose_name_plural = _("AI Conversations")
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['-updated_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title or f'Conversation #{self.id}'} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        """Auto-generates title from first message if empty"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and not self.title:
            # Generate title from first user message
            first_msg = self.messages.filter(role='user').first()
            if first_msg:
                # Truncate to 50 characters
                self.title = first_msg.content[:50] + ('...' if len(first_msg.content) > 50 else '')
                self.save(update_fields=['title'])
    
    @property
    def message_count(self):
        """Total number of messages"""
        return self.messages.count()
    
    @property
    def last_message_at(self):
        """Date of last message"""
        last = self.messages.order_by('-created_at').first()
        return last.created_at if last else self.created_at
    
    def get_context_messages(self, max_messages: int = 10):
        """
        Retrieves the last N messages for LLM context
        
        Args:
            max_messages: Maximum number of messages to include
        
        Returns:
            List of dicts [{role, content}] in OpenAI format
        """
        if not self.enable_history:
            return []
        
        messages = self.messages.order_by('-created_at')[:max_messages]
        # Reverse order (oldest → newest)
        return [
            {'role': msg.role, 'content': msg.content}
            for msg in reversed(messages)
        ]


class Message(models.Model):
    """
    Individual message in a conversation
    Can be type 'user', 'assistant' or 'system'
    """
    ROLE_CHOICES = [
        ('user', _('User')),
        ('assistant', _('AI Assistant')),
        ('system', _('System')),
    ]
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_("Conversation")
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name=_("Role")
    )
    content = models.TextField(
        verbose_name=_("Content")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        db_index=True
    )
    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Tokens Used"),
        help_text=_("Number of tokens generated (assistant only)")
    )
    generation_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Generation Time (s)"),
        help_text=_("Duration in seconds (assistant only)")
    )
    
    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        preview = self.content[:50] + ('...' if len(self.content) > 50 else '')
        return f"[{self.role}] {preview}"
    
    def clean(self):
        """Custom validation"""
        super().clean()
        if not self.content.strip():
            raise ValidationError(_("Content cannot be empty"))
    
    @property
    def is_from_user(self):
        """Check if message is from user"""
        return self.role == 'user'
    
    @property
    def is_from_assistant(self):
        """Check if message is from AI"""
        return self.role == 'assistant'


class ConversationPreference(models.Model):
    """
    User preferences for AI conversations
    Stores user's default settings
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='ia_chat_preferences',
        verbose_name=_("User")
    )
    default_model = models.CharField(
        max_length=50,
        default='llama3',
        verbose_name=_("Default Model"),
        help_text=_("Model used for new conversations")
    )
    default_enable_history = models.BooleanField(
        default=True,
        verbose_name=_("Enable History by Default")
    )
    max_context_messages = models.IntegerField(
        default=10,
        verbose_name=_("Max Context Messages"),
        help_text=_("Number of messages included in context")
    )
    temperature = models.FloatField(
        default=0.7,
        verbose_name=_("Temperature"),
        help_text=_("Response creativity (0.0-1.0)")
    )
    max_tokens = models.IntegerField(
        default=512,
        verbose_name=_("Max Tokens"),
        help_text=_("Maximum response length")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )
    
    class Meta:
        verbose_name = _("Conversation Preference")
        verbose_name_plural = _("Conversation Preferences")
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
    
    def clean(self):
        """Value validation"""
        super().clean()
        if not 0.0 <= self.temperature <= 1.0:
            raise ValidationError(_("Temperature must be between 0.0 and 1.0"))
        if self.max_tokens < 50:
            raise ValidationError(_("max_tokens must be >= 50"))
        if self.max_context_messages < 0:
            raise ValidationError(_("max_context_messages must be >= 0"))
