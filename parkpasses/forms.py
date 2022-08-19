from django.contrib.auth import get_user_model
from django.forms import EmailField, Form

User = get_user_model()


class LoginForm(Form):
    email = EmailField(max_length=254)
