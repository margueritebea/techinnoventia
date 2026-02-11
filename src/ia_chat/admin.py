from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Conversation, Message, ConversationPreference


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'model_used', 'enable_history', 'created_at']
    list_filter = ['model_used', 'enable_history', 'created_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'model_used')
        }),
        (_('Settings'), {
            'fields': ('enable_history',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content']
    readonly_fields = ['created_at', 'tokens_used', 'generation_time']
    
    def content_preview(self, obj):
        return obj.content[:100] + ('...' if len(obj.content) > 100 else '')
    content_preview.short_description = _('Content Preview')


@admin.register(ConversationPreference)
class ConversationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'default_model', 'temperature', 'max_tokens']
    list_filter = ['default_model']
    search_fields = ['user__username']
    fieldsets = (
        (_('User'), {
            'fields': ('user',)
        }),
        (_('Model Settings'), {
            'fields': ('default_model', 'default_enable_history', 'max_context_messages')
        }),
        (_('Generation Parameters'), {
            'fields': ('temperature', 'max_tokens')
        }),
    )
