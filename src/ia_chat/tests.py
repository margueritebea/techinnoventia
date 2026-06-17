"""
Tests for ia_chat app.
Covers: models, REST views, serializers.
LLMService is not loaded — tests run without llama-cpp-python installed.
"""
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Conversation, ConversationPreference, Message

User = get_user_model()

# DRF with CookieJWTAuthentication returns 403 (not 401) for unauthenticated
# requests because the auth class has no www_authenticate_realm.
UNAUTHENTICATED_STATUS = status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _uid():
    """Short unique suffix to avoid username collisions across test classes."""
    return uuid.uuid4().hex[:8]


def make_user(username=None, password='pass1234!'):
    username = username or f'user_{_uid()}'
    return User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password=password,
    )


def make_conversation(user, **kwargs):
    defaults = {'model_used': 'llama3', 'enable_history': True}
    defaults.update(kwargs)
    return Conversation.objects.create(user=user, **defaults)


def make_message(conversation, role='user', content='Hello'):
    return Message.objects.create(
        conversation=conversation, role=role, content=content
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class ConversationModelTest(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_str_without_title(self):
        conv = make_conversation(self.user)
        self.assertIn(str(conv.id), str(conv))

    def test_str_with_title(self):
        conv = make_conversation(self.user, title='Mon test')
        self.assertIn('Mon test', str(conv))

    def test_message_count(self):
        conv = make_conversation(self.user)
        self.assertEqual(conv.message_count, 0)
        make_message(conv)
        self.assertEqual(conv.message_count, 1)

    def test_last_message_at_fallback(self):
        conv = make_conversation(self.user)
        self.assertEqual(conv.last_message_at, conv.created_at)

    def test_last_message_at_with_messages(self):
        conv = make_conversation(self.user)
        msg = make_message(conv)
        self.assertEqual(conv.last_message_at, msg.created_at)

    def test_get_context_messages_returns_openai_format(self):
        conv = make_conversation(self.user)
        make_message(conv, role='user', content='Bonjour')
        make_message(conv, role='assistant', content='Salut !')
        context = conv.get_context_messages(max_messages=10)
        self.assertEqual(len(context), 2)
        self.assertEqual(context[0], {'role': 'user', 'content': 'Bonjour'})

    def test_get_context_messages_disabled_history(self):
        conv = make_conversation(self.user, enable_history=False)
        make_message(conv, role='user', content='Bonjour')
        self.assertEqual(conv.get_context_messages(), [])

    def test_get_context_messages_respects_limit(self):
        conv = make_conversation(self.user)
        for i in range(15):
            make_message(conv, content=f'msg {i}')
        context = conv.get_context_messages(max_messages=5)
        self.assertEqual(len(context), 5)


class MessageModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.conv = make_conversation(self.user)

    def test_is_from_user(self):
        msg = make_message(self.conv, role='user')
        self.assertTrue(msg.is_from_user)
        self.assertFalse(msg.is_from_assistant)

    def test_is_from_assistant(self):
        msg = make_message(self.conv, role='assistant')
        self.assertTrue(msg.is_from_assistant)
        self.assertFalse(msg.is_from_user)

    def test_str_truncates_long_content(self):
        msg = make_message(self.conv, content='A' * 100)
        self.assertIn('[user]', str(msg))
        self.assertIn('...', str(msg))

    def test_empty_content_raises_validation_error(self):
        from django.core.exceptions import ValidationError
        msg = Message(conversation=self.conv, role='user', content='   ')
        with self.assertRaises(ValidationError):
            msg.clean()


class ConversationPreferenceModelTest(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_temperature_validation(self):
        from django.core.exceptions import ValidationError
        pref = ConversationPreference(user=self.user, temperature=1.5)
        with self.assertRaises(ValidationError):
            pref.clean()

    def test_max_tokens_validation(self):
        from django.core.exceptions import ValidationError
        pref = ConversationPreference(user=self.user, max_tokens=10)
        with self.assertRaises(ValidationError):
            pref.clean()

    def test_str(self):
        pref = ConversationPreference.objects.create(user=self.user)
        self.assertIn(self.user.username, str(pref))


# ---------------------------------------------------------------------------
# Signal tests
# ---------------------------------------------------------------------------

class AutoTitleSignalTest(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_title_generated_from_first_user_message(self):
        conv = make_conversation(self.user)
        make_message(conv, role='user', content='Quelle est la capitale de la France ?')
        conv.refresh_from_db()
        self.assertTrue(conv.title)
        self.assertIn('Quelle est la capitale', conv.title)

    def test_title_not_overwritten_when_already_set(self):
        conv = make_conversation(self.user, title='Mon titre')
        make_message(conv, role='user', content='Autre contenu')
        conv.refresh_from_db()
        self.assertEqual(conv.title, 'Mon titre')

    def test_title_truncated_at_50_chars(self):
        conv = make_conversation(self.user)
        long_content = 'A' * 100
        make_message(conv, role='user', content=long_content)
        conv.refresh_from_db()
        self.assertLessEqual(len(conv.title), 53)  # 50 + '...'


# ---------------------------------------------------------------------------
# REST View tests
# ---------------------------------------------------------------------------

class ConversationListViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.other = make_user()
        self.url = reverse('ia_chat:conversation-list')

    def test_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, UNAUTHENTICATED_STATUS)

    def test_returns_only_own_conversations(self):
        own_conv = make_conversation(self.user)
        make_conversation(self.other)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        returned_ids = [c['id'] for c in results]
        self.assertIn(own_conv.id, returned_ids)
        other_conv_ids = list(
            Conversation.objects.filter(user=self.other).values_list('id', flat=True)
        )
        for oid in other_conv_ids:
            self.assertNotIn(oid, returned_ids)

    def test_ordered_by_updated_at_desc(self):
        c1 = make_conversation(self.user, title='First')
        c2 = make_conversation(self.user, title='Second')
        c1.title = 'First updated'
        c1.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        results = response.data['results']
        own_titles = [
            c['title'] for c in results
            if c['id'] in [c1.id, c2.id]
        ]
        self.assertEqual(own_titles[0], 'First updated')


class ConversationDetailViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.other = make_user()
        self.conv = make_conversation(self.user, title='Original')

    def url(self, pk=None):
        return reverse('ia_chat:conversation-detail', kwargs={'pk': pk or self.conv.pk})

    def test_get_own_conversation(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Original')

    def test_get_other_user_conversation_returns_403(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_title(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url(), {'title': 'Nouveau titre'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.conv.refresh_from_db()
        self.assertEqual(self.conv.title, 'Nouveau titre')

    def test_patch_model(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url(), {'model_used': 'mistral'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.conv.refresh_from_db()
        self.assertEqual(self.conv.model_used, 'mistral')

    def test_delete_own_conversation(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Conversation.objects.filter(pk=self.conv.pk).exists())

    def test_delete_other_user_conversation_returns_403(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.delete(self.url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_not_allowed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url(), {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class MessageListViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.other = make_user()
        self.conv = make_conversation(self.user)
        self.msg1 = make_message(self.conv, role='user', content='Question')
        self.msg2 = make_message(self.conv, role='assistant', content='Réponse')

    def url(self, conversation_pk=None):
        return reverse(
            'ia_chat:message-list',
            kwargs={'conversation_pk': conversation_pk or self.conv.pk},
        )

    def test_returns_messages_in_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        returned_ids = [m['id'] for m in results]
        self.assertIn(self.msg1.id, returned_ids)
        self.assertIn(self.msg2.id, returned_ids)
        self.assertLess(
            returned_ids.index(self.msg1.id),
            returned_ids.index(self.msg2.id),
        )

    def test_other_user_cannot_access(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ConversationPreferenceViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.url = reverse('ia_chat:preferences')

    def test_get_creates_default_preferences(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['default_model'], 'llama3')
        self.assertAlmostEqual(float(response.data['temperature']), 0.7)

    def test_patch_temperature(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, {'temperature': 0.3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pref = ConversationPreference.objects.get(user=self.user)
        self.assertAlmostEqual(pref.temperature, 0.3)

    def test_patch_invalid_temperature_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, {'temperature': 2.0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_invalid_max_tokens_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, {'max_tokens': 10})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_not_allowed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AvailableModelsViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.url = reverse('ia_chat:models')

    def test_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, UNAUTHENTICATED_STATUS)

    def test_returns_list_of_dicts(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        # Each item must have the expected keys when llama-cpp-python is installed
        for model in response.data:
            self.assertIn('key', model)
            self.assertIn('name', model)
            self.assertIn('context_size', model)
