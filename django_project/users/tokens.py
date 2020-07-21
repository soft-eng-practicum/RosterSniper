from django.contrib.auth.tokens import PasswordResetTokenGenerator

class ActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"

# We need an instance because PasswordResetTokenGenerator doesn't use static methods
activation_token_generator = ActivationTokenGenerator()
