"""
    This module contains the models required to impliment passes.

    - PassType (Local, Holiday, Annual etc.)
    - PassTypePricingWindow (A period of time that specific pricing can be specified)
    - PassTypePricingWindowOption (The duration options for a pass i.e. 5 days, 14 days, etc.)
    - Pass (The pass itself which contains the information required to generate the QR Code)
"""
import datetime
import logging

import qrcode
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import models

from parkpasses.components.parks.models import Park
from parkpasses.components.passes.utils import PdfGenerator
from parkpasses.settings import PASS_TYPES

logger = logging.getLogger(__name__)


class PassType(models.Model):
    """A class to represent a pass type"""

    image = models.ImageField(null=False, blank=False)
    name = models.CharField(max_length=100)  # Name reserved for system use
    display_name = models.CharField(max_length=50, null=False, blank=False)
    display_order = models.SmallIntegerField(null=False, blank=False)
    display_externally = models.BooleanField(null=False, blank=False, default=True)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"{self.display_name}"


class PassTypePricingWindow(models.Model):
    """A class to represent a pass type pricing window

    The default pricing window for a pass type will have no expiry date
    The system will not allow for each pass type to have more than one
    default pricing window.
    """

    name = models.CharField(max_length=50, null=False, blank=False)
    pass_type = models.ForeignKey(PassType, on_delete=models.PROTECT)
    datetime_start = models.DateTimeField()
    datetime_expiry = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.datetime_expiry:
            default_pricing_window_count = PassTypePricingWindow.objects.filter(
                pass_type=self.pass_type, datetime_expiry__isnull=True
            )
            if default_pricing_window_count > 0:
                raise ValidationError(
                    "There can only be one default pricing window for a pass type. \
                    Default pricing windows are those than have no expiry date."
                )
            else:
                if self.datetime_start > datetime.datetime.now():
                    raise ValidationError(
                        "The default pricing window start date must be in the past."
                    )
        else:
            if self.datetime_start >= self.datetime_expiry:
                raise ValidationError(
                    "The start date must occur before the expiry date."
                )
            if self.datetime_expiry <= datetime.datetime.now():
                raise ValidationError("The expiry date must be in the future.")

        super().save(*args, **kwargs)


class PassTypePricingWindowOption(models.Model):
    """A class to represent a pass type pricing window option"""

    pricing_window = models.ForeignKey(PassTypePricingWindow, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)  # i.e. '5 days'
    duration = models.SmallIntegerField()  # in days i.e. 5, 14, 28, 365
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False, null=False)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"Option: {self.name} | Pricing Window: {self.pricing_window.name} \
            | Pass Type: {self.pricing_window.pass_type.display_name}"


class Pass(models.Model):
    """A class to represent a pass"""

    FUTURE = "FU"
    CURRENT = "CU"
    EXPIRED = "EX"
    CANCELLED = "CA"
    PROCESSING_STATUS_CHOICES = [
        (FUTURE, "Future"),
        (CURRENT, "Current"),
        (EXPIRED, "Expired"),
        (CANCELLED, "Cancelled"),
    ]

    user = models.IntegerField(null=False, blank=False)  # EmailUserRO
    option = models.ForeignKey(PassTypePricingWindowOption, on_delete=models.PROTECT)
    pass_number = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    vehicle_registration_1 = models.CharField(max_length=10, null=True, blank=True)
    vehicle_registration_2 = models.CharField(max_length=10, null=True, blank=True)
    park = models.ForeignKey(Park, on_delete=models.PROTECT, null=True, blank=True)
    datetime_start = models.DateTimeField(null=False, default=False)
    datetime_expiry = models.DateTimeField(null=False, blank=False)
    renew_automatically = models.BooleanField(null=False, blank=False, default=False)
    prevent_further_vehicle_updates = models.BooleanField(
        null=False, blank=False, default=False
    )
    park_pass_pdf = models.FilePathField(null=True, blank=True)
    processing_status = models.CharField(
        max_length=2,
        choices=PROCESSING_STATUS_CHOICES,
    )
    sold_via = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        app_label = "parkpasses"

    def __str__(self):
        return f"{self.pass_number}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def generate_qrcode(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        pass_data_json = serializers.serialize("json", self)
        # replace this line with the real encryption server at a later date
        encrypted_pass_data = self.imaginary_encryption_endpoint(pass_data_json)
        qr.add_data(encrypted_pass_data)
        qr.make(fit=True)
        return qrcode.make_image(fill="black", back_color="white")
        # qr_image.save(park_pass_pdf_path(self, "qrcode.png"))

    def generate_park_pass_pdf(self):
        pdfGenerator = PdfGenerator()
        self.park_pass_pdf = pdfGenerator.generate_park_pass_pdf(self)

    def imaginary_encryption_endpoint(self, json_pass_data):
        return json_pass_data + json_pass_data

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.pass_number == "":
            self.pass_number = f"PP{self.pk:06d}"
            super().save(*args, **kwargs)


class HolidayPassManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("option", "pricing_window", "pass_type")
            .filter(option__pricing_window__pass_type__name=PASS_TYPES.HOLIDAY_PASS)
        )


class HolidayPass(Pass):
    """A proxy class to represent a holiday pass"""

    objects = HolidayPassManager()

    class Meta:
        proxy = True
        app_label = "parkpasses"

    def save(self):
        pass


class LocalParkPassManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("option", "pricing_window", "pass_type")
            .filter(option__pricing_window__pass_type__name=PASS_TYPES.LOCAL_PARK_PASS)
        )


class LocalParkPass(Pass):
    """A proxy class to represent a local park pass"""

    class Meta:
        proxy = True
        app_label = "parkpasses"

    def save(self):
        pass


class GoldStarPassManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("option", "pricing_window", "pass_type")
            .filter(option__pricing_window__pass_type__name=PASS_TYPES.GOLD_STAR_PASS)
        )


class GoldStarPass(Pass):
    """A proxy class to represent a gold star pass"""

    class Meta:
        proxy = True
        app_label = "parkpasses"

    def save(self, *args, **kwargs):
        # if the user does not have a postal address
        # raise a ValidationError exception
        if True:
            raise ValidationError
        super().save(*args, **kwargs)


class DayEntryPassManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("option", "pricing_window", "pass_type")
            .filter(option__pricing_window__pass_type__name=PASS_TYPES.DAY_ENTRY_PASS)
        )


class DayEntryPass(Pass):
    """A proxy class to represent a day entry pass"""

    class Meta:
        proxy = True
        app_label = "parkpasses"

    def save(self):
        pass
