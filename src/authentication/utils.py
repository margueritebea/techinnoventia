# authentication/utils.py
import uuid
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_unique_username(first_name: str, last_name: str, email: str) -> str:
    """
    Génère un username slugifié unique (max 20 chars).
    Si un username existe déjà, on ajoute un suffix numérique.
    """
    base = slugify(f"{first_name} {last_name}".strip())

    if not base and email:
        email_prefix = email.split("@")[0]
        base = slugify(email_prefix)

    if not base:
        base = f"user{uuid.uuid4().hex[:5]}"

    # garder un peu de place pour suffix numérique
    base = base[:15]

    existing_usernames = list(
        User.objects.filter(username__startswith=base).values_list("username", flat=True)
    )

    if base not in existing_usernames:
        return base[:20]

    suffixes = []
    for u in existing_usernames:
        suffix = u.replace(base, "")
        if suffix.isdigit():
            try:
                suffixes.append(int(suffix))
            except ValueError:
                continue

    next_suffix = max(suffixes) + 1 if suffixes else 1
    username = f"{base}{next_suffix}"
    return username[:20]
