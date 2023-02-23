from django.contrib.sessions.models import Session
from django.db import models


class UserSession(models.Model):
    """A way to easily track the sessions for each user so we can
    log a user out of all their sessions when their permission level changes
    in our case when an external user becomes a retailer"""

    user = models.IntegerField(null=False)
    session = models.ForeignKey(Session, null=False, on_delete=models.CASCADE)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"Email User ID: {self.user}. Session key: {self.session}"
