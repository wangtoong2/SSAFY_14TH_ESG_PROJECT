import re

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.utils.text import slugify


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Ensure social signup always produces a valid, unique username.

    Our User model inherits AbstractUser, so username is required and unique.
    Some providers may not supply a suitable username; we derive it from email
    (or provider+uid) and de-duplicate.
    """

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        # Ensure username exists and is unique.
        if not getattr(user, 'username', None):
            email = (data.get('email') or '').strip()
            base = ''
            if email and '@' in email:
                base = email.split('@', 1)[0]

            base = slugify(base) if base else ''
            if not base:
                provider = getattr(sociallogin.account, 'provider', 'social')
                uid = getattr(sociallogin.account, 'uid', 'user')
                base = f"{provider}_{uid}"

            base = re.sub(r'[^a-zA-Z0-9_]+', '_', base).strip('_')
            if not base:
                base = 'user'

            # Keep it reasonably short (AbstractUser.username max_length=150).
            base = base[:60]

            User = get_user_model()
            candidate = base
            i = 0
            while User.objects.filter(username=candidate).exists():
                i += 1
                suffix = str(i)
                candidate = (base[: max(1, 60 - (len(suffix) + 1))] + '_' + suffix)

            user.username = candidate

        # Optionally populate nickname for our custom field.
        if hasattr(user, 'nickname') and not getattr(user, 'nickname', ''):
            user.nickname = (data.get('name') or data.get('given_name') or '').strip()

        return user
