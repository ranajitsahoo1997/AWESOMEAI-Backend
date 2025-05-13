# accounts/tokens.py

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    pass

account_password_reset_token = AccountPasswordResetTokenGenerator()
