from rest_framework import serializers

from .models import Conversation, ConversationPreference, Message


class MessageSerializer(serializers.ModelSerializer):
    """Read-only — messages are created via WebSocket only."""

    class Meta:
        model = Message
        fields = [
            'id', 'role', 'content',
            'tokens_used', 'generation_time', 'created_at',
        ]
        read_only_fields = fields


class ConversationListSerializer(serializers.ModelSerializer):
    """Lightweight representation used for listing conversations."""

    message_count = serializers.IntegerField(read_only=True)
    last_message_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'model_used', 'enable_history',
            'message_count', 'last_message_at', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Full representation — allows updating title, model and history toggle."""

    message_count = serializers.IntegerField(read_only=True)
    last_message_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'model_used', 'enable_history',
            'message_count', 'last_message_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'message_count', 'last_message_at', 'created_at', 'updated_at']


class ConversationPreferenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConversationPreference
        fields = [
            'default_model', 'default_enable_history',
            'max_context_messages', 'temperature', 'max_tokens',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_temperature(self, value):
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError("Temperature must be between 0.0 and 1.0")
        return value

    def validate_max_tokens(self, value):
        if value < 50:
            raise serializers.ValidationError("max_tokens must be >= 50")
        return value

    def validate_max_context_messages(self, value):
        if value < 0:
            raise serializers.ValidationError("max_context_messages must be >= 0")
        return value
