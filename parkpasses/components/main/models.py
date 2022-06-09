import os

from django.db import models

from parkpasses import settings


class RevisionedMixin(models.Model):
    """
    A model tracked by reversion through the save method.
    """

    def save(self, **kwargs):
        from reversion import revisions

        if kwargs.pop("no_revision", False):
            super().save(**kwargs)
        else:
            with revisions.create_revision():
                if "version_user" in kwargs:
                    revisions.set_user(kwargs.pop("version_user", None))
                if "version_comment" in kwargs:
                    revisions.set_comment(kwargs.pop("version_comment", ""))
                super().save(**kwargs)

    @property
    def created_date(self):
        from reversion.models import Version

        return Version.objects.get_for_object(self).last().revision.date_created

    @property
    def modified_date(self):
        from reversion.models import Version

        return Version.objects.get_for_object(self).first().revision.date_created

    class Meta:
        abstract = True


class ApplicationType(models.Model):
    name = models.CharField(
        max_length=64, unique=True, choices=settings.APPLICATION_TYPES
    )
    order = models.PositiveSmallIntegerField(default=0)
    visible = models.BooleanField(default=True)

    application_fee = models.DecimalField(
        "Application Fee", max_digits=6, decimal_places=2, null=True
    )
    oracle_code_application = models.CharField(max_length=50)
    oracle_code_licence = models.CharField(max_length=50)
    is_gst_exempt = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        app_label = "parkpasses"

    @staticmethod
    def get_application_type_by_name(name):
        try:
            return ApplicationType.objects.get(name=name)
        except Exception:
            return None

    @property
    def name_display(self):
        return self.get_name_display()

    @property
    def confirmation_text(self):
        text = ""
        if self.name == "registration_of_interest":
            text = "registration of interest"
        if self.name == "lease_licence":
            text = "lease or licence"
        return text

    def __str__(self):
        return self.name


""" class OracleCode(models.Model):
    CODE_TYPE_CHOICES = (
        (
            settings.APPLICATION_TYPE_REGISTRATION_OF_INTEREST,
            settings.APPLICATION_TYPE_REGISTRATION_OF_INTEREST,
        ),
        (
            settings.APPLICATION_TYPE_LEASE_LICENCE,
            settings.APPLICATION_TYPE_LEASE_LICENCE,
        ),
    )
    code_type = models.CharField(
        "Application Type",
        max_length=64,
        choices=CODE_TYPE_CHOICES,
        default=CODE_TYPE_CHOICES[0][0],
    )
    code = models.CharField(max_length=50, blank=True)
    archive_date = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"{self.code_type} - {self.code}" """


class Question(models.Model):
    CORRECT_ANSWER_CHOICES = (
        ("answer_one", "Answer one"),
        ("answer_two", "Answer two"),
        ("answer_three", "Answer three"),
        ("answer_four", "Answer four"),
    )
    question_text = models.TextField(blank=False)
    answer_one = models.CharField(max_length=200, blank=True)
    answer_two = models.CharField(max_length=200, blank=True)
    answer_three = models.CharField(max_length=200, blank=True)
    answer_four = models.CharField(max_length=200, blank=True)
    correct_answer = models.CharField(
        "Correct Answer",
        max_length=40,
        choices=CORRECT_ANSWER_CHOICES,
        default=CORRECT_ANSWER_CHOICES[0][0],
    )
    application_type = models.ForeignKey(
        ApplicationType, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return self.question_text

    @property
    def correct_answer_value(self):
        return getattr(self, self.correct_answer)


class UserAction(models.Model):
    who = models.IntegerField()  # EmailUserRO
    when = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    what = models.TextField(blank=False)

    def __str__(self):
        return "{what} ({who} at {when})".format(
            what=self.what, who=self.who, when=self.when
        )

    class Meta:
        abstract = True
        app_label = "parkpasses"


class CommunicationsLogEntry(models.Model):
    TYPE_CHOICES = [
        ("email", "Email"),
        ("phone", "Phone Call"),
        ("mail", "Mail"),
        ("person", "In Person"),
        ("onhold", "On Hold"),
        ("onhold_remove", "Remove On Hold"),
        ("with_qaofficer", "With QA Officer"),
        ("with_qaofficer_completed", "QA Officer Completed"),
        ("referral_complete", "Referral Completed"),
    ]
    DEFAULT_TYPE = TYPE_CHOICES[0][0]

    to = models.TextField(blank=True, verbose_name="To")
    fromm = models.CharField(max_length=200, blank=True, verbose_name="From")
    cc = models.TextField(blank=True, verbose_name="cc")

    type = models.CharField(max_length=35, choices=TYPE_CHOICES, default=DEFAULT_TYPE)
    reference = models.CharField(max_length=100, blank=True)
    subject = models.CharField(
        max_length=200, blank=True, verbose_name="Subject / Description"
    )
    text = models.TextField(blank=True)
    customer = models.IntegerField()  # EmailUserRO
    staff = models.IntegerField()  # EmailUserRO

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        app_label = "parkpasses"


class Document(models.Model):
    name = models.CharField(
        max_length=255, blank=True, verbose_name="name", help_text=""
    )
    description = models.TextField(blank=True, verbose_name="description", help_text="")
    uploaded_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "parkpasses"
        abstract = True

    @property
    def path(self):
        if self._file:
            return self._file.path
        else:
            return ""

    @property
    def filename(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename


class GlobalSettings(models.Model):
    keys = (
        # ('credit_facility_link', 'Credit Facility Link'),
        # ('deed_poll', 'Deed poll'),
        # ('deed_poll_filming', 'Deed poll Filming'),
        # ('deed_poll_event', 'Deed poll Event'),
        # ('online_training_document', 'Online Training Document'),
        # ('park_finder_link', 'Park Finder Link'),
        # ('fees_and_charges', 'Fees and charges link'),
        # ('event_fees_and_charges', 'Event Fees and charges link'),
        # ('commercial_filming_handbook', 'Commercial Filming Handbook link'),
        # ('park_stay_link', 'Park Stay Link'),
        # ('event_traffic_code_of_practice', 'Event traffic code of practice'),
        # ('trail_section_map', 'Trail section map'),
        # ('dwer_application_form', 'DWER Application Form'),
    )
    key = models.CharField(
        max_length=255,
        choices=keys,
        blank=False,
        null=False,
    )
    value = models.CharField(max_length=255)

    class Meta:
        app_label = "parkpasses"
        verbose_name_plural = "Global Settings"


class SystemMaintenance(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def duration(self):
        """Duration of system maintenance (in mins)"""
        return (
            int((self.end_date - self.start_date).total_seconds() / 60.0)
            if self.end_date and self.start_date
            else ""
        )

    duration.short_description = "Duration (mins)"

    class Meta:
        app_label = "parkpasses"
        verbose_name_plural = "System maintenance"

    def __str__(self):
        return "System Maintenance: {} ({}) - starting {}, ending {}".format(
            self.name, self.description, self.start_date, self.end_date
        )


class UserSystemSettings(models.Model):
    one_row_per_park = models.BooleanField(default=False)
    user = models.IntegerField(unique=True)  # EmailUserRO
    event_training_completed = models.BooleanField(default=False)
    event_training_date = models.DateField(blank=True, null=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name_plural = "User System Settings"
